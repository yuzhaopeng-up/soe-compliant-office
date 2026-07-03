import sqlite3, os
db = r'C:\Users\于兆鹏\.local\share\TeleAgent\im-service\im-service.db'
if os.path.exists(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for t in cursor.fetchall():
        print('Table:', t[0])
    conn.close()
else:
    print('DB not found')
