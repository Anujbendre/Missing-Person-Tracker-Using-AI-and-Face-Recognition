"""
Example Python script demonstrating how to use the Face Detection & Recognition API
Run this after starting the server with: uvicorn app:app --reload --port 8000
"""

import requests
import os

# Backend URL
BASE_URL = "http://localhost:8000/api/face"


def example_detect_face(image_path: str):
    """Example: Detect faces in an image"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Face Detection")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Prepare request
    url = f"{BASE_URL}/detect-face"
    files = {"file": open(image_path, "rb")}
    data = {
        "engine": "retinaface",  # Options: retinaface, mtcnn, mediapipe
        "crop_faces": "true"
    }
    
    # Send request
    print(f"📤 Sending request to {url}")
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    # Display results
    print(f"\n✅ Status: {result['status']}")
    print(f"📊 Total faces detected: {result['total_faces']}")
    
    for i, face in enumerate(result['faces']):
        print(f"\nFace #{i+1}:")
        print(f"  - Bounding box: {face['bounding_box']}")
        print(f"  - Confidence: {face['confidence']:.2%}")
        print(f"  - Engine: {face['engine']}")
        if 'cropped_face_path' in face:
            print(f"  - Cropped face: {face['cropped_face_path']}")
    
    print(f"\n📁 Image path: {result['image_path']}")


def example_recognize_face(image_path: str):
    """Example: Recognize face from database"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Face Recognition")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Prepare request
    url = f"{BASE_URL}/recognize-face"
    files = {"file": open(image_path, "rb")}
    data = {
        "model_name": "VGG-Face",  # Options: VGG-Face, Facenet, OpenFace, ArcFace
        "threshold": "70"
    }
    
    # Send request
    print(f"📤 Sending request to {url}")
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    # Display results
    print(f"\n✅ Status: {result['status']}")
    
    if result['match_found']:
        print(f"🎯 MATCH FOUND!")
        print(f"  - Name: {result['name']}")
        print(f"  - Person ID: {result['person_id']}")
        print(f"  - Match percentage: {result['match_percentage']:.2f}%")
        
        if 'all_matches' in result:
            print(f"\n📋 All matches:")
            for match in result['all_matches']:
                print(f"  - {match['name']}: {match['match_percentage']:.2f}%")
    else:
        print(f"❌ No match found")
        print(f"  - Message: {result['message']}")


def example_analyze_face(image_path: str):
    """Example: Analyze face attributes"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Face Attribute Analysis")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Prepare request
    url = f"{BASE_URL}/analyze-face"
    files = {"file": open(image_path, "rb")}
    data = {"analyze_attributes": "true"}
    
    # Send request
    print(f"📤 Sending request to {url}")
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    # Display results
    if 'attributes' in result:
        attrs = result['attributes']
        print(f"\n✅ Face Attributes:")
        print(f"  - Age: {attrs.get('age', 'Unknown')}")
        print(f"  - Gender: {attrs.get('gender', 'Unknown')}")
        print(f"  - Emotion: {attrs.get('emotion', 'Unknown')}")
        print(f"  - Race: {attrs.get('race', 'Unknown')}")


def example_verify_faces(image1_path: str, image2_path: str):
    """Example: Verify if two faces match"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Face Verification")
    print("="*60)
    
    if not os.path.exists(image1_path):
        print(f"❌ Image 1 not found: {image1_path}")
        return
    
    if not os.path.exists(image2_path):
        print(f"❌ Image 2 not found: {image2_path}")
        return
    
    # Prepare request
    url = f"{BASE_URL}/verify-faces"
    files = {
        "file1": open(image1_path, "rb"),
        "file2": open(image2_path, "rb")
    }
    data = {"model_name": "VGG-Face"}
    
    # Send request
    print(f"📤 Sending request to {url}")
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    # Display results
    print(f"\n✅ Verification Result:")
    print(f"  - Verified: {result['verified']}")
    print(f"  - Match percentage: {result['match_percentage']:.2f}%")
    print(f"  - Distance: {result['distance']:.4f}")
    print(f"  - Threshold: {result['threshold']:.4f}")


def example_load_database():
    """Example: Load face database"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Load Face Database")
    print("="*60)
    
    url = f"{BASE_URL}/load-database"
    data = {
        "database_path": "dataset/missing_persons",
        "model_name": "VGG-Face"
    }
    
    print(f"📤 Sending request to {url}")
    response = requests.post(url, data=data)
    result = response.json()
    
    print(f"\n✅ Status: {result['status']}")
    print(f"📊 Total faces loaded: {result['total_faces']}")


def example_get_supported_models():
    """Example: Get supported models"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Get Supported Models")
    print("="*60)
    
    url = f"{BASE_URL}/supported-models"
    
    print(f"📤 Sending request to {url}")
    response = requests.get(url)
    result = response.json()
    
    print(f"\n✅ Detection Engines:")
    for engine in result['detection_engines']:
        print(f"  - {engine}")
    
    print(f"\n✅ Recognition Models:")
    for model in result['recognition_models']:
        print(f"  - {model}")
    
    print(f"\n✅ Analysis Attributes:")
    for attr in result['analysis_attributes']:
        print(f"  - {attr}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("FACE DETECTION & RECOGNITION API - PYTHON EXAMPLES")
    print("="*60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/supported-models")
        if response.status_code != 200:
            print("❌ Server is not running!")
            print("Start the server with: uvicorn app:app --reload --port 8000")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("Start the server with: uvicorn app:app --reload --port 8000")
        return
    
    print("✅ Server is running!")
    
    # Sample image path (update this to your image)
    sample_image = "dataset/missing_persons/person_101.jpg"
    
    if not os.path.exists(sample_image):
        print(f"\n⚠️ Sample image not found: {sample_image}")
        print("Please update the sample_image path in this script")
        print("Or add images to dataset/missing_persons/ folder")
        return
    
    # Run examples
    example_detect_face(sample_image)
    example_recognize_face(sample_image)
    example_analyze_face(sample_image)
    example_load_database()
    example_get_supported_models()
    
    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
