"""
Diagnostic script to check face detection in your database images
This will help you understand why faces aren't being detected
"""

import os
import cv2
from ai.advanced_face_detection import AdvancedFaceDetector
from ai.face_detection import FaceDetector

def check_database_images():
    """Check all images in your uploads folder for detectable faces"""
    
    print("=" * 70)
    print("DATABASE IMAGE DIAGNOSTIC TOOL")
    print("=" * 70)
    
    # Check uploads folder
    uploads_folder = "uploads"
    if not os.path.exists(uploads_folder):
        print(f"❌ Uploads folder not found: {uploads_folder}")
        return
    
    # Get all image files
    image_files = []
    for root, dirs, files in os.walk(uploads_folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_files.append(os.path.join(root, file))
    
    print(f"\n📁 Found {len(image_files)} images in uploads folder\n")
    
    if len(image_files) == 0:
        print("⚠️ No images found! Please add images to the uploads folder.")
        return
    
    # Test with YOLO first
    print("=" * 70)
    print("TESTING WITH YOLOv8 (Recommended)")
    print("=" * 70)
    
    try:
        yolo_detector = AdvancedFaceDetector(engine='yolov8')
        yolo_results = []
        
        for img_path in image_files[:10]:  # Test first 10 images
            faces = yolo_detector.detect_faces(img_path)
            yolo_results.append((img_path, len(faces)))
            
            status = "✅" if len(faces) > 0 else "❌"
            print(f"{status} {img_path}: {len(faces)} face(s)")
        
        yolo_success = sum(1 for _, count in yolo_results if count > 0)
        print(f"\n📊 YOLO Results: {yolo_success}/{len(yolo_results)} images with faces")
        
    except Exception as e:
        print(f"❌ YOLO failed: {e}")
        yolo_results = []
    
    # Test with OpenCV (fallback)
    print("\n" + "=" * 70)
    print("TESTING WITH OPENCV (Fallback)")
    print("=" * 70)
    
    opencv_detector = FaceDetector()
    opencv_results = []
    
    for img_path in image_files[:10]:  # Test first 10 images
        faces = opencv_detector.detect_faces(img_path)
        opencv_results.append((img_path, len(faces)))
        
        status = "✅" if len(faces) > 0 else "❌"
        print(f"{status} {img_path}: {len(faces)} face(s)")
    
    opencv_success = sum(1 for _, count in opencv_results if count > 0)
    print(f"\n📊 OpenCV Results: {opencv_success}/{len(opencv_results)} images with faces")
    
    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    
    print(f"YOLOv8:  {yolo_success}/{len(yolo_results)} images detected")
    print(f"OpenCV:  {opencv_success}/{len(opencv_results)} images detected")
    
    if yolo_success > opencv_success:
        print(f"\n✅ YOLOv8 is better! Using {yolo_success - opencv_success} more images")
    elif opencv_success > yolo_success:
        print(f"\n⚠️ OpenCV detected more faces (unusual)")
    else:
        print(f"\n📊 Both detectors found the same number of faces")
    
    # Show image details
    print("\n" + "=" * 70)
    print("IMAGE DETAILS")
    print("=" * 70)
    
    for img_path in image_files[:5]:
        try:
            img = cv2.imread(img_path)
            if img is not None:
                h, w, c = img.shape
                size_kb = os.path.getsize(img_path) / 1024
                print(f"\n📷 {img_path}")
                print(f"   Size: {w}x{h} pixels")
                print(f"   File size: {size_kb:.1f} KB")
                print(f"   Channels: {c}")
            else:
                print(f"\n❌ Cannot read: {img_path}")
        except Exception as e:
            print(f"\n❌ Error reading {img_path}: {e}")

def check_specific_image(image_path):
    """Test face detection on a specific image"""
    
    print("=" * 70)
    print(f"TESTING SPECIFIC IMAGE: {image_path}")
    print("=" * 70)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Check image properties
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Cannot read image: {image_path}")
        return
    
    h, w, c = img.shape
    size_kb = os.path.getsize(image_path) / 1024
    
    print(f"\n📷 Image Properties:")
    print(f"   Dimensions: {w}x{h} pixels")
    print(f"   File size: {size_kb:.1f} KB")
    print(f"   Channels: {c}")
    
    # Test with YOLO
    print("\n" + "-" * 70)
    print("YOLOv8 Detection:")
    print("-" * 70)
    
    try:
        yolo_detector = AdvancedFaceDetector(engine='yolov8')
        yolo_faces = yolo_detector.detect_faces(image_path)
        
        if len(yolo_faces) > 0:
            print(f"✅ YOLO detected {len(yolo_faces)} face(s)")
            for i, face in enumerate(yolo_faces):
                x, y, w, h = face['bounding_box']
                conf = face['confidence']
                print(f"   Face {i+1}: ({x}, {y}, {w}, {h}) - Confidence: {conf:.2%}")
        else:
            print(f"❌ YOLO detected 0 faces")
    except Exception as e:
        print(f"❌ YOLO failed: {e}")
    
    # Test with OpenCV
    print("\n" + "-" * 70)
    print("OpenCV Detection:")
    print("-" * 70)
    
    opencv_detector = FaceDetector()
    opencv_faces = opencv_detector.detect_faces(image_path)
    
    if len(opencv_faces) > 0:
        print(f"✅ OpenCV detected {len(opencv_faces)} face(s)")
        for i, (x, y, w, h) in enumerate(opencv_faces):
            print(f"   Face {i+1}: ({x}, {y}, {w}, {h})")
    else:
        print(f"❌ OpenCV detected 0 faces")
    
    # Save visualization
    print("\n" + "-" * 70)
    print("Creating Visualization:")
    print("-" * 70)
    
    try:
        yolo_detector = AdvancedFaceDetector(engine='yolov8')
        output_path = image_path.replace('.jpg', '_detected.jpg').replace('.png', '_detected.png')
        success = yolo_detector.draw_detections(image_path, output_path)
        
        if success:
            print(f"✅ Saved visualization to: {output_path}")
            print(f"   Open this file to see detected faces!")
        else:
            print(f"❌ Failed to create visualization")
    except Exception as e:
        print(f"❌ Visualization failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific image
        image_path = sys.argv[1]
        check_specific_image(image_path)
    else:
        # Check all database images
        check_database_images()
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)
    print("\n💡 Tips:")
    print("   1. If YOLO detects faces but OpenCV doesn't → Use YOLO (already configured!)")
    print("   2. If neither detects faces → Images may not contain clear faces")
    print("   3. For best results, use clear, front-facing photos")
    print("   4. Test a specific image: python diagnose_faces.py path/to/image.jpg")
