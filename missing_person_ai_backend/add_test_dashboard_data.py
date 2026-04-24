from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

print("\n=== Adding Test Data to Dashboard ===\n")

# Insert test detection logs
cursor.execute("""
    INSERT INTO detection_logs (image_path, matched_person_id, matched_name, confidence, status) 
    VALUES 
    ('uploads/face_uploads/test1.jpg', 101, 'Person 101', 85.50, 'MATCH FOUND'),
    ('uploads/face_uploads/test2.jpg', 102, 'Person 102', 78.30, 'MATCH FOUND'),
    ('uploads/face_uploads/test3.jpg', 103, 'Person 103', 92.10, 'MATCH FOUND')
""")
print("✅ Added 3 detection logs")

# Insert test alerts
cursor.execute("""
    INSERT INTO detection_alerts (person_id, frame_id, confidence, alert_message, is_read) 
    VALUES 
    (101, 1, 85.50, 'AI match found for Person 101', 0),
    (102, 2, 78.30, 'AI match found for Person 102', 0),
    (103, 3, 92.10, 'AI match found for Person 103', 0)
""")
print("✅ Added 3 alerts")

conn.commit()

# Verify
cursor.execute('SELECT COUNT(*) FROM detection_logs')
print(f"\n📊 Total detection_logs: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM detection_logs WHERE status = 'MATCH FOUND'")
print(f"🎯 MATCH FOUND: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM detection_alerts WHERE is_read = 0')
print(f"🔔 Unread alerts: {cursor.fetchone()[0]}")

cursor.close()
conn.close()

print("\n✅ Dashboard data added successfully!")
print("💡 Refresh your police dashboard to see the updated statistics!")
