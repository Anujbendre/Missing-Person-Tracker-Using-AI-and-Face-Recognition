# 📸 Quick Setup Guide for Testing Face Recognition

## Current Status

✅ **Working:**
- 1 missing person with photo: `test5` (20260412_121708_39d4226d.jpg)
- 10 CCTV images available for scanning

❌ **Missing Photos:**
- Test1: needs `20260411_212604.jpg`
- test2: needs `Screenshot 2026-03-29 125430.png`
- Test3: needs `WIN_20260411_23_23_41_Pro.jpg` (✅ Now copied!)
- test4: needs `WIN_20260411_23_23_41_Pro.jpg` (✅ Now copied!)

## Quick Test (Recommended)

### Option 1: Test with Existing Data
You currently have:
- **1 missing person** with photo (test5)
- **10 CCTV images** to scan

**Steps:**
1. Go to AI Recognition page
2. Select **test5** from Missing Persons tab
3. Select any CCTV image from CCTV Images tab
4. Click "Scan Selected Image"
5. Check backend logs for results

**Note:** This probably won't match unless the CCTV image contains the same person as test5.

### Option 2: Create a Perfect Test Case (Best for Demo)

**Step 1: Take a Photo**
1. Take a clear, front-facing photo of yourself or a friend
2. Save it as `person_test.jpg`

**Step 2: Add as Missing Person**
1. Copy the photo to uploads folder:
   ```
   Copy-Item "person_test.jpg" "uploads\person_test.jpg"
   ```

2. Add to database (run this Python script):
   ```python
   import mysql.connector
   
   conn = mysql.connector.connect(
       host='localhost',
       user='root',
       password='AnujBendre_9890_anuj',
       database='missing_person_ai'
   )
   cursor = conn.cursor()
   
   cursor.execute("""
       INSERT INTO missing_persons (full_name, age, gender, last_seen_location, photo_path, status)
       VALUES (%s, %s, %s, %s, %s, %s)
   """, ('Test Person', 25, 'Male', 'Test Location', 'person_test.jpg', 'MISSING'))
   
   conn.commit()
   print(f"✅ Added missing person with ID: {cursor.lastrowid}")
   conn.close()
   ```

**Step 3: Create CCTV Version**
1. Take another photo of the SAME person (different angle/lighting is OK)
2. Save it as `cctv_test.jpg`
3. Copy to CCTV folder:
   ```
   Copy-Item "cctv_test.jpg" "uploads\cctv\cctv_test.jpg"
   ```

**Step 4: Add CCTV Image to Database**
Run this script:
```python
import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='AnujBendre_9890_anuj',
    database='missing_person_ai'
)
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO camera_frames (image_path, camera_location, captured_at, processed)
    VALUES (%s, %s, %s, %s)
""", ('uploads/cctv/cctv_test.jpg', 'Test Camera', datetime.now(), 0))

conn.commit()
print("✅ Added CCTV image to database")
conn.close()
```

**Step 5: Test the Match!**
1. Go to AI Recognition page
2. Select "Test Person" from Missing Persons
3. Select the CCTV image from CCTV Images
4. Click "Scan Selected Image"
5. **Should find a match!** ✅

## Option 3: Use Sample Photos

If you don't want to take photos, you can:

1. Download sample face photos from the internet
2. Use the same photo for both missing person AND CCTV (perfect match)
3. This will test if the system works correctly

## Expected Results

When scanning the SAME person:
- **Similarity Score:** > 0.5 (50%)
- **Confidence:** > 45%
- **Status:** "MATCH FOUND" ✅

When scanning DIFFERENT people:
- **Similarity Score:** < 0.5 (50%)
- **Confidence:** < 45%
- **Status:** "NOT FOUND" ❌

## Current Files Available

### In uploads/:
- ✅ 20260412_121708_39d4226d.jpg (test5's photo)
- ✅ WIN_20260411_23_23_41_Pro.jpg (Test3 & test4's photo)

### In uploads/cctv/:
- ✅ 20260412_124005.jpg
- ✅ 20260412_124019.jpg
- ✅ 20260412_124022.jpg

### In cctv_images/:
- ✅ 10 CCTV images available

## Troubleshooting

**Problem:** "No face detected"
**Solution:** Use photos with clear, front-facing faces

**Problem:** "Photo not found"
**Solution:** Make sure photo file exists in `uploads/` folder

**Problem:** "NOT FOUND" when scanning same person
**Solution:** 
- Photos might be too different
- Try with more similar photos
- Check backend logs for similarity score

## Need Help?

Check the backend terminal when scanning. You'll see detailed logs like:
```
🔍 Detected 1 face(s) in CCTV image
✅ Using face at position: [234, 160, 192, 192]
🔍 Face comparison similarity: 0.7234 (threshold: 0.5)
✅ Potential match: Test Person
```

This tells you exactly what's happening!
