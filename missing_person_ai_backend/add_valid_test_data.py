from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

print("\n=== Checking existing person IDs ===\n")
cursor.execute("SELECT person_id, full_name FROM missing_persons")
persons = cursor.fetchall()
print(f"Found {len(persons)} persons:")
for p in persons:
    print(f"  - person_id: {p[0]}, name: {p[1]}")

print("\n=== Adding Test Data with Valid Person IDs ===\n")

if len(persons) > 0:
    # Use actual person IDs from the database
    person_ids = [p[0] for p in persons[:3]]  # Get first 3
    person_names = [p[1] for p in persons[:3]]
    
    # Insert detection logs with valid person IDs
    for i, (pid, pname) in enumerate(zip(person_ids, person_names), 1):
        cursor.execute("""
            INSERT INTO detection_logs (image_path, matched_person_id, matched_name, confidence, status) 
            VALUES (%s, %s, %s, %s, 'MATCH FOUND')
        """, (f'uploads/face_uploads/test{i}.jpg', pid, pname, 85.0 + i))
        print(f"✅ Added detection log for {pname} (ID: {pid})")
        
        # Insert alert
        cursor.execute("""
            INSERT INTO detection_alerts (person_id, frame_id, confidence, alert_message, is_read) 
            VALUES (%s, %s, %s, %s, 0)
        """, (pid, i, 85.0 + i, f'AI match found for {pname}'))
        print(f"✅ Added alert for {pname}")

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
