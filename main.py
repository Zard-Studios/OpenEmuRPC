import threading, time, sqlite3, os, sys, datetime, platform
if not sys.platform.startswith('darwin'):
    sys.exit('OpenEmu is a macOS exclusive application.')

import rumps, presence, Quartz, AppKit

appName = 'OpenEmu'

path = os.path.expanduser('~/Library/Application Support/OpenEmuRPC')
emupath = os.path.expanduser('~/Library/Application Support/OpenEmu/Game Library')

class Client(rumps.App):
    def __init__(self):
        try:
            if not self.check_permissions():
                self.request_permissions()
                self.handle_error('Failed to receive permissions.', True)
        except AttributeError as error:
            ver = platform.mac_ver()[0].split('.')
            if ver[0] == '10' and int(ver[1]) < 15:
                print('running pre-screen-recording permissions macos')
            else:
                raise error
        self.rpc = None
        self.games = None
        self.connect()
        super().__init__('OpenEmuRPC', title = '🎮')
        threading.Thread(target = self.background, daemon = True).start()

    def connect(self):
        try:
            self.rpc = presence.Client('1469721500604043462')
        except (ConnectionRefusedError, FileNotFoundError):
            pass

    def handle_error(self, error:Exception, quit:bool):
        if not os.path.isdir(path):
            os.mkdir(path)
        with open(f'{path}/error.txt', 'a') as file:
            file.write('[%s] %s\n' % (datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), error))
        print(error)
        if quit:
            rumps.alert('Error in OpenEmuRPC', '"%s"' % error)
            sys.exit()
        rumps.notification('Error in OpenEmuRPC', 'Make an issue if error persists', '"%s"' % error)

    def check_permissions(self):
        return Quartz.CGPreflightScreenCaptureAccess()

    def request_permissions(self):
        Quartz.CGRequestScreenCaptureAccess()

    def is_running(self):
        apps = AppKit.NSWorkspace.sharedWorkspace().launchedApplications()
        for app in apps:
            if app['NSApplicationName'] == appName:
                return True
        return False

    libretro_map = {
        'openemu.system.snes': 'Nintendo - Super Nintendo Entertainment System',
        'openemu.system.nes': 'Nintendo - Nintendo Entertainment System',
        'openemu.system.gb': 'Nintendo - Game Boy',
        'openemu.system.gbc': 'Nintendo - Game Boy Color',
        'openemu.system.gba': 'Nintendo - Game Boy Advance',
        'openemu.system.n64': 'Nintendo - Nintendo 64',
        'openemu.system.ds': 'Nintendo - Nintendo DS',
        'openemu.system.ps1': 'Sony - PlayStation',
        'openemu.system.genesis': 'Sega - Mega Drive - Genesis',
        'openemu.system.master': 'Sega - Master System',
        'openemu.system.gamegear': 'Sega - Game Gear',
        'openemu.system.psp': 'Sony - PlayStation Portable',
        'openemu.system.pce': 'NEC - PC Engine - TurboGrafx 16',
        'openemu.system.pc-fx': 'NEC - PC-FX',
        'openemu.system.saturn': 'Sega - Saturn',
        'openemu.system.dreamcast': 'Sega - Dreamcast',
        'openemu.system.gamecube': 'Nintendo - GameCube',
        'openemu.system.wii': 'Nintendo - Wii',
    }

    def update(self):
        if not self.rpc:
            self.connect()
            return
        
        if not self.is_running():
            try:
                self.rpc.update()
            except:
                pass
            return
        windows = self.get_windows()
        menus = False
        data = {}
        for i in ('Library', 'Gameplay', 'Controls', 'Cores', 'System Files', 'Shader Parameters'):
            if i in windows:
                menus = i
                windows.remove(i)
        for i in ('', 'Apple', 'About', 'Updating OpenEmu', 'File', 'Edit', 'View', 'Window', 'Help'):
            if i in windows:
                windows.remove(i)
        if windows and windows != [appName]:
            if self.games != windows:
                self.start = round(time.time())
                self.games = windows.copy()
            data['start'] = self.start
            if appName in windows:
                windows.remove(appName)
            
            game_title = windows[0]
            game_info = self.get_game_info(game_title)
            
            data['details'] = 'Playing %s' % game_title
            data['large_text'] = game_title
            data["status_display_type"] = presence.StatusDisplayType.DETAILS

            if game_info:
                system_id = game_info.get('system_id', '')
                art_url = game_info.get('art_url')
                
                if art_url and 'gamespot.com' not in art_url:
                    data['large_image'] = art_url
                elif system_id in self.libretro_map:
                    lr_system = self.libretro_map[system_id]
                    safe_title = "".join([c if c not in '&*/:<>?\\|' else '_' for c in game_title])
                    data['large_image'] = f"https://thumbnails.libretro.com/{lr_system}/Named_Boxarts/{safe_title}.png"
                
                if system_id:
                    icon_name = system_id.replace('openemu.system.', '')
                    data['small_image'] = icon_name
                    data['small_text'] = game_info.get('system_name', icon_name).capitalize()

            if menus:
                data['state'] = 'In %s menu...' % menus
        
        for key in list(data):
            if isinstance(data[key], str):
                if len(data[key]) < 2:
                    del data[key]
                elif len(data[key]) > 128:
                    data[key] = data[key][:128]
        if data:
            try:
                self.rpc.update(presence.Presence(**data))
            except Exception as e:
                pass
        else:
            self.rpc.update()

    def get_game_info(self, title:str):
        try:
            db_file = os.path.join(emupath, 'Library.storedata')
            if not os.path.exists(db_file):
                return None
            con = sqlite3.connect(db_file)
            cursor = con.cursor()

            cursor.execute('''
                SELECT g.Z_PK, g.ZGAMETITLE, s.ZSYSTEMIDENTIFIER, s.ZLASTLOCALIZEDNAME, i.ZSOURCE
                FROM ZGAME g
                LEFT JOIN ZSYSTEM s ON g.ZSYSTEM = s.Z_PK
                LEFT JOIN ZIMAGE i ON g.Z_PK = i.ZBOX
                WHERE g.ZGAMETITLE IS NOT NULL
            ''')
            rows = cursor.fetchall()
            con.close()

            for zpk, gtitle, sys_id, sys_name, art_url in rows:
                if title.lower() in gtitle.lower() or gtitle.lower() in title.lower():
                    return {
                        'zpk': zpk,
                        'title': gtitle,
                        'system_id': sys_id,
                        'system_name': sys_name,
                        'art_url': art_url
                    }
            return None
        except:
            return None

    def get_windows(self):
        response = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListExcludeDesktopElements|Quartz.kCGWindowListOptionOnScreenOnly,Quartz.kCGNullWindowID)
        windows = []
        for window in response:
            if window[Quartz.kCGWindowOwnerName] == appName:
                windows.append(window.get(Quartz.kCGWindowName, '<no name>'))
        while '' in windows:
            windows.remove('')
        return windows

    def background(self):
        while True:
            try:
                self.update()
            except Exception as e:
                print(f"Update error: {e}")
            time.sleep(15)

if __name__ == '__main__':
    Client().run()
