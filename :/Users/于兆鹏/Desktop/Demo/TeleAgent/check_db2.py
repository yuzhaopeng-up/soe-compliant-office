import sqlite3
db = r'C:\Users\于兆鹏\.local\share\TeleAgent\im-service\im-service.db'
conn = sqlite3.connect(db)
cursor = conn.cursor()
cursor.execute("SELECT content FROM im_message WHERE content LIKE '%ghp_%' OR content LIKE '%GITHUB_TOKEN%' OR content LIKE '%github_pat_%' LIMIT 5")
for row in cursor.fetchall():
    content = str(row[0])
    idx = content.find('ghp_')
    if idx == -1:
        idx = content.find('GITHUB_TOKEN')
    if idx >= 0:
        print('MATCH at index', idx, ':', content[max(0,idx-20):idx+50])
conn.close()
