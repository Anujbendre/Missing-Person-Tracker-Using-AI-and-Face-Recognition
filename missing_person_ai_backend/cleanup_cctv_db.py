import mysql.connector
import os

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='AnujBendre_9890_anuj',
    database='missing_person_ai'
)
cursor = conn.cursor(dictionary=True)

# Get all camera frames
cursor.execute("SELECT id, image_path FROM camera_frames ORDER BY id DESC")
frames = cursor.fetchall()

print(f"📊 Total database entries: {len(frames)}\n")

deleted_count = 0
found_count = 0

for frame in frames:
    image_path = frame['image_path']
    
    # Remove prefix if exists
    if image_path.startswith('uploads/cctv/'):
        filename = image_path.replace('uploads/cctv/', '')
    elif image_path.startswith('cctv/'):
        filename = image_path.replace('cctv/', '')
    else:
        filename = image_path
    
    # Check both folders
    new_path = os.path.join('uploads/cctv', filename)
    old_path = os.path.join('cctv_images', filename)
    
    if os.path.exists(new_path) or os.path.exists(old_path):
        found_count += 1
    else:
        # File doesn't exist, delete database entry
        print(f"❌ Deleting orphaned entry #{frame['id']}: {image_path}")
        cursor.execute("DELETE FROM camera_frames WHERE id = %s", (frame['id'],))
        conn.commit()
        deleted_count += 1

print(f"\n✅ Cleanup Complete!")
print(f"   Found: {found_count} valid entries")
print(f"   Deleted: {deleted_count} orphaned entries")
print(f"   Remaining: {found_count} entries")

cursor.close()
conn.close()

