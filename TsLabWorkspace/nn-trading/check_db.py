import sqlite3

conn = sqlite3.connect(r'C:\Users\i59400f\.local\share\mimocode\mimocode.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

# Check recent sessions
if 'session' in tables:
    cursor.execute("SELECT id, title, time_created FROM session ORDER BY time_created DESC LIMIT 5")
    print("\nRecent sessions:")
    for row in cursor.fetchall():
        print(f"  {row}")

# Check messages for patterns
if 'message' in tables:
    cursor.execute("SELECT COUNT(*) FROM message")
    print(f"\nTotal messages: {cursor.fetchone()[0]}")

conn.close()
