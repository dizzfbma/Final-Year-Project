import sqlite3

conn = sqlite3.connect("/home/spinn/final-year-project/database/cowrie_events.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

cursor.execute("SELECT * FROM sessions LIMIT 10;")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT 40;")
for row in cursor.fetchall():
    print(row)


conn.close()
