import cv2
import os
from database import get_db_connection
from alerts.alert_service import create_alert
from ai.deepface_recognition import DeepFaceRecognizer, recognize_face_deepface

DATASET_PATH = "dataset/missing_persons"


# ============================
# FACE RECOGNITION FROM IMAGE
# ============================

def recognize_face(image_path):
  """
  Recognize face using DeepFace (Deep Learning)
  Uses pre-trained CNN models: VGG-Face, Facenet, ArcFace, etc.
  """
  try:
    # Check if dataset exists
    if not os.path.exists(DATASET_PATH):
      return {"match_found": False, "error": "Dataset not found"}
    
    # Use DeepFace for recognition (Deep Learning approach)
    # You can change model_name to: 'VGG-Face', 'Facenet', 'OpenFace', 'ArcFace'
    # Facenet and ArcFace are generally more accurate
    result = recognize_face_deepface(image_path, model='Facenet', threshold=60)
    
    if result.get("match_found"):
      person_id = result.get('person_id')
      confidence = result.get('match_percentage', 0)
      
      camera_id = 1  # example camera
      
      match_id = create_match_log(person_id, camera_id, confidence)
      
      create_alert(match_id, police_user_id=1)
      
      return {
        "match_found": True,
        "person_id": person_id,
        "match_id": match_id,
        "confidence": confidence,
        "name": result.get('name', 'Unknown'),
        "method": "DeepFace (Deep Learning)"
      }
    
    return {"match_found": False, "method": "DeepFace (Deep Learning)"}
    
  except Exception as e:
    print(f"Error in face recognition: {e}")
    import traceback
    traceback.print_exc()
    return {"match_found": False, "error": str(e)}


# ============================
# VIDEO FACE SCAN
# ============================

def recognize_video(video_path):

    cap = cv2.VideoCapture(video_path)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        temp_image = "temp_frame.jpg"
        cv2.imwrite(temp_image, frame)

        result = recognize_face(temp_image)

        if result.get("match_found"):

            cap.release()

            return result

    cap.release()

    return {"match_found": False}


# ============================
# LIVE CAMERA SCAN
# ============================

def live_camera_scan():

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        cv2.imshow("Live Camera Scan", frame)

        temp_image = "live_frame.jpg"
        cv2.imwrite(temp_image, frame)

        result = recognize_face(temp_image)

        if result.get("match_found"):

            cap.release()
            cv2.destroyAllWindows()

            return result

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    return {"match_found": False}


def create_match_log(person_id, camera_id, confidence):
  conn = get_db_connection()
  cursor = conn.cursor()

  query = """
    INSERT INTO match_logs (person_id, camera_id, confidence)
    VALUES (%s, %s, %s)
    """

  cursor.execute(query, (person_id, camera_id, confidence))
  conn.commit()

  match_id = cursor.lastrowid

  cursor.close()
  conn.close()

  return match_id
