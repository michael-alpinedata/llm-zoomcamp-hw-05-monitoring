import sqlite3

conn = sqlite3.connect("traces.db")
# divide by 1 M to be in milliseconds
cur = conn.execute("""
    SELECT input_tokens FROM spans WHERE name = 'llm';
""")
for row in cur.fetchall():
    print(row)