import sqlite3

conn = sqlite3.connect("traces.db")
cur = conn.execute("SELECT DISTINCT name FROM spans;")
for row in cur.fetchall():
    print(row)