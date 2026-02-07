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

    def update(self):
        if not self.is_running():
            self.rpc.update()
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
            game = windows[0]
            art = self.get_artwork(windows[0])
            if art:
                data['large_image'] = art
            if len(windows) > 1:
                game = ', '.join(windows)
                art = self.get_artwork(windows[1])
                if art:
                    data['small_image'] = art
                    data['small_text'] = windows[1]
            data['details'] = 'Playing %s' % game
            data["status_display_type"] = presence.StatusDisplayType.DETAILS
            data['large_text'] = windows[0]
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
                self.handle_error(f"RPC Update failed: {e}", False)
        else:
            self.rpc.update()

    def get_artwork(self, title:str):
        try:
            db_file = os.path.join(emupath, 'Library.storedata')
            if not os.path.exists(db_file):
                return None
            con = sqlite3.connect(db_file)
            cursor = con.cursor()

            cursor.execute('SELECT ZBOX, ZSOURCE FROM ZIMAGE WHERE ZSOURCE IS NOT NULL')
            art = {i[0]: i[1] for i in cursor.fetchall()}
            
            cursor.execute('SELECT Z_PK, ZGAMETITLE FROM ZGAME')
            games = cursor.fetchall()
            con.close()

            for zpk, gtitle in games:
                if not gtitle:
                    continue
                if title.lower() in gtitle.lower() or gtitle.lower() in title.lower():
                    return art.get(zpk)
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
            self.update()
            time.sleep(1)

if __name__ == '__main__':
    Client().run()
