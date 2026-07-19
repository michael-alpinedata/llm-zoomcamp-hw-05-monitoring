import sqlite3

conn = sqlite3.connect("traces.db")
# divide by 1 M to be in milliseconds
cur = conn.execute("""
    SELECT name, SUM(end_time - start_time)/1000000. AS total_duration
    FROM spans
    WHERE name != 'rag'
    GROUP BY name;
""")
for row in cur.fetchall():
    print(row)