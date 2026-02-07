import sqlite3, os

emupath = os.path.expanduser('~/Library/Application Support/OpenEmu/Game Library')
db_path = os.path.join(emupath, 'Library.storedata')

con = sqlite3.connect(db_path)
cursor = con.cursor()

# Get systems
cursor.execute("SELECT Z_PK, ZNAME FROM ZSYSTEM")
systems = cursor.fetchall()
print("\nSystems (ZSYSTEM):")
for pk, name in systems:
    print(f"PK: {pk}, Name: {name}")

# Get games and their system ID
cursor.execute("SELECT Z_PK, ZGAMETITLE, ZSYSTEM FROM ZGAME LIMIT 5")
games = cursor.fetchall()
print("\nGames with System ID (ZGAME):")
for pk, title, sys_id in games:
    print(f"Game: {title}, System ID: {sys_id}")

con.close()
