import sqlite3
db = r'C:\Users\于兆鹏\.local\share\TeleAgent\im-service\im-service.db'
conn = sqlite3.connect(db)
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(im_message)')
for col in cursor.fetchall():
    print(col)
cursor.execute('PRAGMA table_info(im_channel_profile)')
for col in cursor.fetchall():
    print(col)
conn.close()
