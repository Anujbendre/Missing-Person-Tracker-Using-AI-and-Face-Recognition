"""
Quick script to sync CCTV images from folder to database
Run this when CCTV images are not showing in AI Recognition page
"""
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
skipped_count = 0

# Scan uploads/cctv folder
print("📁 Scanning uploads/cctv folder...")
if os.path.exists('uploads/cctv'):
    for filename in os.listdir('uploads/cctv'):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = f"uploads/cctv/{filename}"
            # Check if already in database
            cursor.execute("SELECT id FROM camera_frames WHERE image_path = %s", (image_path,))
            if not cursor.fetchone():
                # Add to database 
                cursor.execute(
                    "INSERT INTO camera_frames (image_path, camera_location, captured_at, processed) VALUES (%s, %s, %s, %s)",
                    (image_path, "CCTV Camera", datetime.now(), 0)
                )
                conn.commit()
                print(f"✅ Added: {filename}")
                added_count += 1
            else:
                print(f"⏭️  Already exists: {filename}")
                skipped_count += 1
else:
    print("❌ uploads/cctv folder not found!")

print(f"\n✅ Sync Complete!")
print(f"   Added: {added_count} new images")
print(f"   Skipped: {skipped_count} existing images")

cursor.close()
conn.close()
