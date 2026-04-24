"""
Check database images and help add proper face images
"""

import os
import cv2
from ai.yolo_face_detection import YOLOFaceDetector

def check_database_images():
    """Check if database images have detectable faces"""
    print("\n" + "="*60)
    print("CHECKING DATABASE IMAGES")
    print("="*60)
    
    db_path = "dataset/missing_persons"
    detector = YOLOFaceDetector(model_size='n', confidence_threshold=0.3)
    
    files = os.listdir(db_path)
    image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"\n📁 Found {len(image_files)} images in database/")
    print("-"*60)
    
    for img_file in image_files:
        img_path = os.path.join(db_path, img_file)
        
        # Check file size
        file_size = os.path.getsize(img_path) / 1024  # KB
        print(f"\n🖼️  {img_file} ({file_size:.1f} KB)")
        
        # Read image
        img = cv2.imread(img_path)
        if img is None:
            print(f"   ❌ Could not read image")
            continue
        
        height, width = img.shape[:2]
        print(f"   📐 Size: {width}x{height} pixels")
        
        # Detect faces
        faces = detector.detect_faces(img_path)
        
        if len(faces) > 0:
            print(f"   ✅ Detected {len(faces)} face(s)")
            for i, face in enumerate(faces):
                bbox = face['bounding_box']
                conf = face['confidence']
                print(f"      Face {i+1}: confidence={conf:.4f}, size={bbox[2]}x{bbox[3]}")
        else:
            print(f"   ❌ No faces detected!")
            print(f"   💡 This image needs a clear, front-facing photo")


def create_test_database():
    """Create a test by copying face_uploads to database"""
    print("\n" + "="*60)
    print("CREATING TEST DATABASE")
    print("="*60)
    
    import shutil
    
    face_uploads = "uploads/face_uploads"
    db_path = "dataset/missing_persons"
    
    if not os.path.exists(face_uploads):
        print(f"❌ Directory not found: {face_uploads}")
        return
    
    files = os.listdir(face_uploads)
    image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if len(image_files) == 0:
        print("❌ No images in face_uploads")
        return
    
    print(f"\n📋 Available images to add to database:")
    for i, img_file in enumerate(image_files, 1):
        print(f"   {i}. {img_file}")
    
    print(f"\n💡 To add images to database:")
    print(f"   1. Copy images from uploads/face_uploads/ to dataset/missing_persons/")
    print(f"   2. Rename them as: person_103.jpg, person_104.jpg, etc.")
    print(f"   3. Make sure they have clear, front-facing photos")
    
    # Ask if user wants to copy first image as test
    if len(image_files) > 0:
        print(f"\n🧪 Would you like to copy the first image as a test?")
        print(f"   This will create person_103.jpg in database")
        
        # Copy the file
        src = os.path.join(face_uploads, image_files[0])
        dst = os.path.join(db_path, "person_103.jpg")
        
        shutil.copy2(src, dst)
        print(f"\n✅ Copied {image_files[0]} → person_103.jpg")
        print(f"   Now you can test recognition with this image!")


if __name__ == "__main__":
    check_database_images()
    create_test_database()
