from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

print("\n=== DATABASE STATISTICS ===\n")

cursor.execute('SELECT COUNT(*) FROM detection_logs')
print(f"detection_logs: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM detection_logs WHERE status = 'MATCH FOUND'")
print(f"MATCH FOUND: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM detection_alerts WHERE is_read = 0")
print(f"Unread alerts: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM missing_persons")
print(f"Missing persons: {cursor.fetchone()[0]}")

print("\n=== SAMPLE DETECTION LOGS ===")
cursor.execute("SELECT id, person_id, status, confidence FROM detection_logs LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(f"  {row}")

cursor.close()
conn.close()
