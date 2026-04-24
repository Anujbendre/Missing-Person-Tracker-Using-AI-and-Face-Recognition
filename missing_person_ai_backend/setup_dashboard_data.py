from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

print("\n=== Creating match_logs table ===")
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            person_id VARCHAR(50) NOT NULL,
            camera_id INT,
            confidence DECIMAL(5,2),
            match_image VARCHAR(255),
            cctv_image VARCHAR(255),
            status ENUM('MATCH FOUND', 'NO MATCH', 'PENDING') DEFAULT 'MATCH FOUND',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_person_id (person_id),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✅ match_logs table created")
except Exception as e:
    print(f"⚠️ match_logs table error: {e}")

print("\n=== Checking detection_alerts structure ===")
cursor.execute("DESCRIBE detection_alerts")
columns = cursor.fetchall()
print("Columns in detection_alerts:")
for col in columns:
    print(f"  {col}")

print("\n=== Creating detection_logs table ===")
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detection_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            person_id VARCHAR(50),
            camera_id INT,
            confidence DECIMAL(5,2),
            status ENUM('MATCH FOUND', 'NO MATCH', 'PENDING') DEFAULT 'PENDING',
            image_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_status (status),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✅ detection_logs table created")
except Exception as e:
    print(f"⚠️ detection_logs table error: {e}")

print("\n=== Inserting test data ===")
try:
    # Insert test detection logs
    cursor.execute("""
        INSERT INTO detection_logs (person_id, camera_id, confidence, status) VALUES
        ('person_101', 1, 85.50, 'MATCH FOUND'),
        ('person_102', 2, 78.30, 'MATCH FOUND'),
        ('person_103', 1, 92.10, 'MATCH FOUND')
    """)
    print("✅ Test detection logs inserted")
except Exception as e:
    print(f"⚠️ Detection logs insert error: {e}")

try:
    # Check what columns detection_alerts has
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'detection_alerts' AND TABLE_SCHEMA = 'missing_person_ai'")
    alert_columns = [col[0] for col in cursor.fetchall()]
    
    if 'is_read' in alert_columns:
        # Insert test alerts
        cursor.execute("""
            INSERT INTO detection_alerts (police_user_id, message, is_read) VALUES
            (1, 'AI match found for person_101 with 85.50% confidence', 0),
            (1, 'AI match found for person_102 with 78.30% confidence', 0),
            (1, 'AI match found for person_103 with 92.10% confidence', 0)
        """)
        print("✅ Test alerts inserted")
    else:
        print("⚠️ detection_alerts doesn't have is_read column")
except Exception as e:
    print(f"⚠️ Alerts insert error: {e}")

conn.commit()

print("\n=== Final Statistics ===")
cursor.execute('SELECT COUNT(*) FROM detection_logs')
print(f"detection_logs: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM detection_logs WHERE status = 'MATCH FOUND'")
print(f"MATCH FOUND: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM detection_alerts WHERE is_read = 0")
print(f"Unread alerts: {cursor.fetchone()[0]}")

cursor.close()
conn.close()

print("\n✅ Database setup complete!")
