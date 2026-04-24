import mysql.connector
import os
from datetime import datetime

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='AnujBendre_9890_anuj',
    database='missing_person_ai'
)
cursor = conn.cursor()

added_count = 0

# Scan uploads/cctv folder
print("📁 Scanning uploads/cctv folder...")
if os.path.exists('uploads/cctv'):
    for filename in os.listdir('uploads/cctv'):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            # Check if already in database
            cursor.execute("SELECT id FROM camera_frames WHERE image_path = %s", (f"uploads/cctv/{filename}",))
            if not cursor.fetchone():
                # Add to database
                cursor.execute(
                    "INSERT INTO camera_frames (image_path, camera_location, captured_at, processed) VALUES (%s, %s, %s, %s)",
                    (f"uploads/cctv/{filename}", "CCTV Camera", datetime.now(), 0)
                )
                conn.commit()
                print(f"✅ Added: {filename}")
                added_count += 1

# Scan cctv_images folder
print("\n📁 Scanning cctv_images folder...")
if os.path.exists('cctv_images'):
    for filename in os.listdir('cctv_images'):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            # Check if already in database
            cursor.execute("SELECT id FROM camera_frames WHERE image_path = %s", (f"cctv_images/{filename}",))
            if not cursor.fetchone():
                # Add to database
                cursor.execute(
                    "INSERT INTO camera_frames (image_path, camera_location, captured_at, processed) VALUES (%s, %s, %s, %s)",
                    (f"cctv_images/{filename}", "CCTV Camera", datetime.now(), 0)
                )
                conn.commit()
                print(f"✅ Added: {filename}")
                added_count += 1

print(f"\n✅ Database Sync Complete!")
print(f"   Added: {added_count} new entries")

cursor.close()
conn.close()
