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

print("🔍 Checking for filename typos in database...\n")

# Get all missing persons
cursor.execute("SELECT person_id, full_name, photo_path FROM missing_persons WHERE photo_path IS NOT NULL")
persons = cursor.fetchall()

fixed_count = 0

for person in persons:
    original_path = person['photo_path']
    new_path = original_path
    needs_fix = False
    
    # Fix common typos
    # 1. Fix .jppg -> .jpg
    if '.jppg' in original_path:
        new_path = original_path.replace('.jppg', '.jpg')
        needs_fix = True
        print(f"📝 Fixing .jppg typo: {original_path} -> {new_path}")
    
    # 2. Fix double digits in dates like 20260411_23_233_41 -> 20260411_23_23_41
    import re
    # Pattern: extra digit in time portion
    if re.search(r'_\d{2}_\d{3}_\d{2}', original_path):
        new_path = re.sub(r'_(\d{2})_(\d{2})(\d)_(\d{2})', r'_\1_\2_\4', original_path)
        needs_fix = True
        print(f"📝 Fixing double digit typo: {original_path} -> {new_path}")
    
    # 3. Fix Screenshot dates like 2026-033-29 -> 2026-03-29
    if re.search(r'\d{4}-\d{3}-\d{2}', original_path):
        new_path = re.sub(r'(\d{4})-(\d{2})\d-(\d{2})', r'\1-\2-\3', original_path)
        needs_fix = True
        print(f"📝 Fixing date typo: {original_path} -> {new_path}")
    
    # Check if file exists with new path
    if needs_fix:
        full_path = os.path.join('uploads', new_path)
        if os.path.exists(full_path):
            print(f"✅ File exists: {full_path}")
            cursor.execute(
                "UPDATE missing_persons SET photo_path = %s WHERE person_id = %s",
                (new_path, person['person_id'])
            )
            conn.commit()
            fixed_count += 1
        else:
            print(f"❌ File still not found: {full_path}")

print(f"\n✅ Fixed {fixed_count} entries")

# Show current status
cursor.execute("SELECT person_id, full_name, photo_path FROM missing_persons")
persons = cursor.fetchall()
print(f"\n📊 Current missing persons in database:")
for p in persons:
    exists = os.path.exists(os.path.join('uploads', p['photo_path']))
    status = "✅" if exists else "❌"
    print(f"  {status} {p['full_name']}: {p['photo_path']}")

cursor.close()
conn.close()
