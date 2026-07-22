import sqlite3

conn = sqlite3.connect("knowledge.db")
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT * FROM tool_invocations"
).fetchall()

for row in rows:
    print(dict(row))