import sqlite3
db = r'C:\Users\于兆鹏\.local\share\TeleAgent\im-service\im-service.db'
conn = sqlite3.connect(db)
cursor = conn.cursor()
cursor.execute("SELECT inbound_text, outbound_text FROM im_message WHERE inbound_text LIKE '%ghp_%' OR outbound_text LIKE '%ghp_%' OR inbound_text LIKE '%GITHUB_TOKEN%' OR outbound_text LIKE '%GITHUB_TOKEN%' LIMIT 5")
for row in cursor.fetchall():
    for i, field in enumerate(row):
        if 'ghp_' in str(field):
            idx = str(field).find('ghp_')
            print(f'Field {i}: ...{str(field)[max(0,idx-10):idx+50]}...')
        if 'GITHUB_TOKEN' in str(field):
            idx = str(field).find('GITHUB_TOKEN')
            print(f'Field {i}: ...{str(field)[max(0,idx-10):idx+60]}...')
conn.close()
