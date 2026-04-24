from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from passlib.context import CryptContext
from pydantic import BaseModel
import shutil
import os
import mysql.connector
from mysql.connector import pooling
import random
import hashlib
import bcrypt
import base64
from datetime import datetime
from jose import jwt
# import cv2
# import numpy as np

# Import face API routes
from ai.face_api_routes import router as face_router

# Import SMS service
from utils.sms_service import sms_service


# ================= APP =================
app = FastAPI(title="Missing Person AI Backend")

# Include face detection and recognition routes
app.include_router(face_router)

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= FILE STORAGE =================
# Separate folders for different image types
UPLOAD_FOLDER = "uploads"  # Missing person photos
CCTV_FOLDER = "uploads/cctv"  # CCTV captured images
AI_IMAGES_FOLDER = "uploads/ai_images"  # AI recognition input
RECOGNIZED_FOLDER = "uploads/recognized"  # Annotated output

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CCTV_FOLDER, exist_ok=True)
os.makedirs(AI_IMAGES_FOLDER, exist_ok=True)
os.makedirs(RECOGNIZED_FOLDER, exist_ok=True)

# Mount all folders for static file serving
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")
# Note: /cctv mount removed, using explicit route below instead

# ================= MIDDLEWARE FOR STATIC FILES CORS =================
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Only add CORP header for static files (CORS is already handled by CORSMiddleware)
    if request.url.path.startswith("/cctv/") or request.url.path.startswith("/uploads/"):
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    
    return response

# ================= CCTV IMAGE SERVING ROUTE =================
@app.get("/cctv/{filename:path}")
async def serve_cctv_image(filename: str):
    """Serve CCTV images with proper CORS headers"""
    import mimetypes
    
    # Handle paths with subfolders like "uploads/cctv/file.jpg" or "cctv_images/file.jpg"
    # Extract just the filename if it contains path separators
    if '/' in filename or '\\' in filename:
        filename = filename.replace('uploads/cctv/', '').replace('cctv_images/', '').replace('cctv/', '')
        filename = filename.split('/')[-1].split('\\')[-1]  # Get just the filename
    
    # Try new location first (uploads/cctv)
    file_path = os.path.join(CCTV_FOLDER, filename)
    
    # If not found, try old location (cctv_images)
    if not os.path.exists(file_path):
        old_cctv_folder = "cctv_images"
        file_path = os.path.join(old_cctv_folder, filename)
    
    if not os.path.exists(file_path):
        print(f"❌ Image not found: {filename}")
        print(f"   Tried: {os.path.join(CCTV_FOLDER, filename)}")
        print(f"   Tried: {os.path.join('cctv_images', filename)}")
        raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "image/jpeg"
    
    print(f"✅ Serving CCTV image: {file_path}")
    
    # Read file and return with CORS headers
    from fastapi.responses import Response
    with open(file_path, "rb") as f:
        content = f.read()
    
    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Cross-Origin-Resource-Policy": "cross-origin",
            "Cache-Control": "public, max-age=3600"
        }
    )

# ================= JWT CONFIG =================
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def create_token(user_data: dict):
    """Create JWT token for user"""
    from datetime import timedelta
    payload = {
        "user_id": user_data.get("user_id"),
        "role_id": user_data.get("role_id"),
        "role_name": user_data.get("role_name"),
        "email": user_data.get("email"),
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# ================= MYSQL CONNECTION POOL =================
# Create connection pool for faster database access
db_pool = pooling.MySQLConnectionPool(
    pool_name="missing_person_pool",
    pool_size=10,
    pool_reset_session=True,
    host="localhost",
    user="root",
    password="AnujBendre_9890_anuj",
    database="missing_person_ai"
)

def get_db_connection():
    """Get connection from pool for faster access"""
    return db_pool.get_connection()

# ================= OTP MODELS =================
class OTPRequest(BaseModel):
    mobile: str

class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: int

otp_store = {}

# ================= PASSWORD =================
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
  # ✅ Convert long password to fixed length
  password = hashlib.sha256(password.encode()).hexdigest()

  # ✅ Then bcrypt
  return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password, hashed_password):
  # ✅ Convert long password to fixed length
  plain_password = hashlib.sha256(plain_password.encode()).hexdigest()

  return bcrypt.checkpw(plain_password.encode(),
                        hashed_password.encode() if isinstance(hashed_password, str) else hashed_password)
# ================= LOGIN MODEL =================
class LoginRequest(BaseModel):
    email: str
    password: str

# ================= SIGNUP =================
@app.post("/police/signup")
def police_signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    mobile: str = Form(...),
    station_name: str = Form(...)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return {"error": "Email already exists"}

        hashed_password = hash_password(password)

        cursor.execute("""
            INSERT INTO users
            (full_name, email, password_hash, mobile, station_name, role_name, role_id, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, email, hashed_password, mobile, station_name, "Police", 2, 1))

        conn.commit()
        
        # Send SMS notification
        try:
            sms_result = sms_service.send_registration_success_sms(
                phone=mobile,
                name=name,
                role="Police Officer"
            )
            
            if sms_result['success']:
                print(f"✅ Registration SMS sent to {mobile}")
            else:
                print(f"⚠️ Failed to send SMS to {mobile}: {sms_result['message']}")
        except Exception as sms_error:
            print(f"⚠️ SMS error (registration still successful): {str(sms_error)}")
        
        return {"message": "Police Registered Successfully", "sms_sent": True}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

# ================= LOGIN =================
@app.post("/police/login")
def police_login(data: LoginRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND role_name='Police'",
            (data.email,)
        )

        user = cursor.fetchone()

        if not user:
            print(f"❌ User not found: {data.email}")
            return {"error": "User not found"}

        print(f"✅ User found: {user.get('email')}, role_id: {user.get('role_id')}")

        if not verify_password(data.password, user["password_hash"]):
            print(f"❌ Wrong password for: {data.email}")
            return {"error": "Wrong password"}

        print(f"✅ Password verified for: {data.email}")

        # Generate JWT token
        try:
            token = create_token({
                "user_id": user["user_id"],
                "role_id": user["role_id"],
                "role_name": user["role_name"],
                "email": user["email"]
            })
            print(f"✅ Token generated successfully")
        except Exception as token_error:
            print(f"❌ Token generation error: {str(token_error)}")
            import traceback
            traceback.print_exc()
            return {"error": f"Token generation failed: {str(token_error)}"}

        response_data = {
            "message": "Login success",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "user_id": user["user_id"],
                "name": user["full_name"],
                "email": user["email"],
                "station": user["station_name"],
                "role_id": user["role_id"],
                "role_name": user["role_name"]
            }
        }
        
        print(f"✅ Login successful, returning response with access_token")
        
        # Send SMS notification for login
        try:
            mobile = user.get("mobile")
            if mobile:
                sms_result = sms_service.send_login_success_sms(
                    phone=mobile,
                    name=user["full_name"],
                    role="Police Officer"
                )
                
                if sms_result['success']:
                    print(f"✅ Login SMS sent to {mobile}")
                    response_data["sms_sent"] = True
                else:
                    print(f"⚠️ Failed to send login SMS to {mobile}: {sms_result['message']}")
                    response_data["sms_sent"] = False
            else:
                print(f"⚠️ No mobile number found for user {user['email']}")
                response_data["sms_sent"] = False
        except Exception as sms_error:
            print(f"⚠️ SMS error (login still successful): {str(sms_error)}")
            response_data["sms_sent"] = False
        
        return response_data

    except Exception as e:
        print(f"❌ Login exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

# ================= CITIZEN SIGNUP =================
@app.post("/citizen/signup")
def citizen_signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    mobile: str = Form(...)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return {"error": "Email already exists"}

        hashed_password = hash_password(password)

        cursor.execute("""
            INSERT INTO users
            (full_name, email, password_hash, mobile, role_name, role_id, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, hashed_password, mobile, "Citizen", 1, 1))

        conn.commit()
        
        # Send SMS notification
        try:
            sms_result = sms_service.send_registration_success_sms(
                phone=mobile,
                name=name,
                role="Citizen"
            )
            
            if sms_result['success']:
                print(f"✅ Registration SMS sent to {mobile}")
            else:
                print(f"⚠️ Failed to send SMS to {mobile}: {sms_result['message']}")
        except Exception as sms_error:
            print(f"⚠️ SMS error (registration still successful): {str(sms_error)}")
        
        return {"message": "Citizen Registered Successfully", "sms_sent": True}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

# ================= GET STATIONS =================
@app.get("/stations")
def get_stations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT station_name FROM police_stations")
    data = cursor.fetchall()

    conn.close()
    return data

# ================= ADD MISSING PERSON =================
@app.post("/api/missing")
async def report_missing(
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(None),
    location: str = Form(None),
    description: str = Form(""),
    reporter_name: str = Form(...),
    reporter_mobile: str = Form(...),
    file: UploadFile = File(None)
):
    try:
        filename = None
        encoding_list = None

        # ================= SAVE IMAGE =================
        if file:
            # Generate unique filename to avoid conflicts
            import uuid
            from datetime import datetime
            
            # Get file extension
            file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
            
            # Create unique filename: timestamp_uuid.extension
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
            
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            filename = unique_filename
            print(f"✅ Image saved: {unique_filename} at {file_path}")
        else:
            print("⚠️ No image uploaded")

        # ================= DATABASE =================
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO missing_persons
        (full_name, age, gender, last_seen_location, description,
         photo_path, face_encoding, status, reporter_name, reporter_mobile)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            age,
            gender,
            location,
            description,
            filename,
            str(encoding_list),
            "MISSING",
            reporter_name,
            reporter_mobile
        ))

        conn.commit()

        return {
            "message": "Report saved successfully",
            "file": filename,
            "photo_path": f"/uploads/{filename}" if filename else None
        }

    except Exception as e:
        print(f"❌ Error in report_missing: {str(e)}")
        return {"error": str(e)}

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
# ================= GET ALL CASES =================
@app.get("/api/all-cases")
def all_cases():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM missing_persons ORDER BY person_id DESC")
        data = cursor.fetchall()

        conn.close()
        return {"data": data}
    except Exception as e:
        print(f"❌ Error in /api/all-cases: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "data": []}

# ================= GET SINGLE CASE BY ID =================
@app.get("/api/case/{case_id}")
def get_single_case(case_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Only fetch required fields for better performance
        cursor.execute(""" 
            SELECT person_id, full_name, age, gender, last_seen_location, 
                   description, photo_path, status, reporter_name, 
                   reporter_mobile, last_seen_date, created_at 
            FROM missing_persons 
            WHERE person_id = %s
        """, (case_id,))
        case = cursor.fetchone()

        conn.close()

        if not case:
            return {"error": "Case not found", "data": None}

        return {"data": case}

    except Exception as e:
        return {"error": str(e)}

# ================= SEND OTP =================
@app.post("/send-otp")
def send_otp(data: OTPRequest):
    otp = random.randint(1000, 9999)
    otp_store[data.mobile] = otp

    print(f"📲 OTP for {data.mobile}: {otp}")

    return {"message": "OTP sent", "otp": otp}

@app.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest):

    if data.mobile not in otp_store:
        raise HTTPException(status_code=400, detail="OTP not found")

    if otp_store[data.mobile] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    mobile = int(data.mobile.strip())

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM missing_persons
        WHERE reporter_mobile = %s
    """, (mobile,))

    cases = cursor.fetchall()

    print("Mobile:", mobile)
    print("Cases:", cases)

    cursor.close()
    conn.close()

    if not cases:
        return {"exists": False, "data": []}

    return {"exists": True, "data": cases}



# ================= UPDATE CASE STATUS =================
from pydantic import BaseModel

class UpdateStatusRequest(BaseModel):
    status: str
    note: str = ""
    updated_by: str = "System"

@app.put("/api/update-case/{case_id}")
def update_case(case_id: int, data: UpdateStatusRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get old status
        cursor.execute("SELECT status FROM missing_persons WHERE person_id = %s", (case_id,))
        old_record = cursor.fetchone()

        if not old_record:
            return {"error": "Case not found"}

        old_status = old_record["status"]
        new_status = data.status

        # Update status
        cursor.execute("""
            UPDATE missing_persons
            SET status = %s
            WHERE person_id = %s
        """, (new_status, case_id))

        # Log history
        cursor.execute("""
            INSERT INTO case_status_history
            (person_id, old_status, new_status, note, updated_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (case_id, old_status, new_status, data.note, data.updated_by))

        conn.commit()

        return {
            "message": "Status updated successfully",
            "old_status": old_status,
            "new_status": new_status
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

# ================= GET CASE HISTORY =================
@app.get("/api/case-history/{case_id}")
def get_case_history(case_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM case_status_history
            WHERE person_id = %s
            ORDER BY created_at DESC
        """, (case_id,))

        history = cursor.fetchall()

        return {"data": history}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


# ================= FEATURE 4: CCTV CAMERA MANAGEMENT =================
class CameraRequest(BaseModel):
    location_name: str
    latitude: float = None
    longitude: float = None
    status: str = "ACTIVE"

@app.post("/api/add-camera")
def add_camera(data: CameraRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cctv_cameras (location_name, latitude, longitude, status)
            VALUES (%s, %s, %s, %s)
        """, (data.location_name, data.latitude, data.longitude, data.status))

        conn.commit()
        return {"message": "Camera added successfully", "camera_id": cursor.lastrowid}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

@app.get("/api/cameras")
def get_cameras():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM cctv_cameras ORDER BY created_at DESC")
        cameras = cursor.fetchall()

        return {"data": cameras}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

@app.put("/api/camera/{camera_id}")
def update_camera(camera_id: int, data: CameraRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE cctv_cameras
            SET location_name=%s, latitude=%s, longitude=%s, status=%s
            WHERE camera_id=%s
        """, (data.location_name, data.latitude, data.longitude, data.status, camera_id))

        conn.commit()
        return {"message": "Camera updated successfully"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

@app.delete("/api/camera/{camera_id}")
def delete_camera(camera_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cctv_cameras WHERE camera_id=%s", (camera_id,))
        conn.commit()

        return {"message": "Camera deleted successfully"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


# ================= APPLY FIR =================
@app.post("/api/fir")
async def apply_fir(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    incident_type: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    accused: str = Form(None),
    delay_reason: str = Form(None),
    property: str = Form(None),
    date: str = Form(None),
    time: str = Form(None)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO fir_cases
        (full_name, email, phone, incident_type, location, description,
         accused, delay_reason, property, date, time)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (full_name, email, phone, incident_type, location, description,
              accused, delay_reason, property, date, time))

        conn.commit()

        return {"message": "FIR submitted successfully"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


# ================= GET ALL FIR =================
@app.get("/api/fir")
def get_firs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM fir_cases ORDER BY fir_id DESC")
    firs = cursor.fetchall()

    return {"data": firs}


# ================= SAVE CCTV FRAME =================
from pydantic import BaseModel

class FrameData(BaseModel):
    image: str

@app.post("/api/save-frame")
async def save_frame(data: dict):
    try:
        print("🔥 API HIT - Saving CCTV frame")  # DEBUG

        image_data = data.get("image")

        if not image_data:
            return {"error": "No image received"}

        # ✅ remove base64 header
        if "," in image_data:
            header, encoded = image_data.split(",", 1)
        else:
            encoded = image_data

        # ✅ decode
        image_bytes = base64.b64decode(encoded)

        # ✅ filename - save to CCTV folder
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        file_path = os.path.join(CCTV_FOLDER, filename)

        # ✅ save file
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        print("✅ CCTV Image saved:", file_path)  # DEBUG

        # ✅ SAVE TO DB - store with cctv/ prefix for proper URL
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO camera_frames (image_path, camera_location) VALUES (%s, %s)",
            (filename, "CCTV Camera")
        )

        conn.commit()

        print("✅ DB saved")  # DEBUG

        return {"message": "Frame saved", "file": filename}

    except Exception as e:
        print("❌ ERROR:", str(e))  # DEBUG
        return {"error": str(e)}

@app.get("/api/frames")
def get_frames():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM camera_frames ORDER BY id DESC")
    frames = cursor.fetchall()
    
    # Add uploads/cctv/ prefix to image paths for proper URL resolution
    for frame in frames:
        if frame.get('image_path') and not frame['image_path'].startswith('uploads/cctv/'):
            frame['image_path'] = 'uploads/cctv/' + frame['image_path']
    
    cursor.close()
    conn.close()
    return {"data": frames}


@app.post("/detect-image")
def detect_image(data: dict):
    """Optimized face detection and matching using YOLOv8 + Advanced Detection"""
    import cv2
    import numpy as np
    from ai.advanced_face_detection import AdvancedFaceDetector
    from ai.face_detection import FaceDetector
    import time

    start_time = time.time()
    conn = None
    cursor = None

    try:
        # ================= VALIDATE INPUT =================
        if "image_path" not in data:
            return {"error": "image_path is required", "status": "ERROR"}

        # Handle both uploads/cctv/ and uploads/ paths
        image_path_rel = data["image_path"]
        if image_path_rel.startswith("uploads/cctv/"):
            image_path = os.path.join(CCTV_FOLDER, image_path_rel.replace("uploads/cctv/", ""))
        elif image_path_rel.startswith("cctv/"):
            # Legacy support
            image_path = os.path.join(CCTV_FOLDER, image_path_rel.replace("cctv/", ""))
        else:
            image_path = os.path.join(UPLOAD_FOLDER, image_path_rel)

        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return {"error": "Image not found", "status": "ERROR"}

        # ================= INITIALIZE DETECTOR (YOLO first, fallback to OpenCV) =================
        try:
            # Try YOLO/Advanced detection first (higher accuracy)
            detector = AdvancedFaceDetector(engine='yolov8')
            faces = detector.detect_faces(image_path)
            use_advanced = True
            print(f"🚀 Using YOLOv8 for face detection")
        except Exception as e:
            print(f"⚠️ YOLO failed, falling back to OpenCV: {e}")
            detector = FaceDetector()
            faces = detector.detect_faces(image_path)
            use_advanced = False
            print(f"🔍 Using OpenCV for face detection")
        
        # Convert faces format if using advanced detector
        if use_advanced and len(faces) > 0:
            # Advanced detector returns list of dicts, extract bounding boxes
            face_boxes = [face['bounding_box'] for face in faces]
            print(f"🔍 Detected {len(faces)} face(s) in CCTV image using YOLOv8")
        else:
            face_boxes = faces
            print(f"🔍 Detected {len(faces)} face(s) in CCTV image")
        
        if len(face_boxes) == 0:
            print(f"❌ No faces detected in: {image_path}")
            return {"status": "No face detected", "message": "No faces found in the image. Please ensure the image contains a clear, front-facing person."}

        # Use the first detected face
        face_box = face_boxes[0]
        print(f"✅ Using face at position: {face_box}")
        
        # Extract target face features ONCE
        target_img = cv2.imread(image_path)
        target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
        x, y, w, h = face_box
        target_face = target_gray[y:y+h, x:x+w]
        target_features = cv2.resize(target_face, (100, 100))
        
        # Calculate histogram ONCE
        target_hist = cv2.calcHist([target_features], [0], None, [256], [0, 256])
        cv2.normalize(target_hist, target_hist)
        
        # ================= DATABASE =================
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT person_id, full_name, photo_path 
            FROM missing_persons
            WHERE photo_path IS NOT NULL
            LIMIT 50
        """)
        persons = cursor.fetchall()

        if not persons:
            return {"status": "ERROR", "message": "No persons in database"}

        print(f"🔍 Scanning {len(persons)} persons...")

        # ================= OPTIMIZED MATCHING =================
        best_match = None
        best_confidence = 0
        match_attempts = 0
        face_detected_count = 0

        for person in persons:
            try:
                person_photo_path = os.path.join(UPLOAD_FOLDER, person["photo_path"])
                
                if not os.path.exists(person_photo_path):
                    print(f"⚠️ Photo not found for {person['full_name']}: {person_photo_path}")
                    continue

                match_attempts += 1
                
                # Detect face in person photo using same engine
                if use_advanced:
                    person_faces_result = detector.detect_faces(person_photo_path)
                    if len(person_faces_result) > 0:
                        face_detected_count += 1
                        # Get bounding box from first face
                        person_bbox = person_faces_result[0]['bounding_box']
                        px, py, pw, ph = person_bbox
                        
                        # Extract and compare
                        person_img = cv2.imread(person_photo_path)
                        person_gray = cv2.cvtColor(person_img, cv2.COLOR_BGR2GRAY)
                        person_face = person_gray[py:py+ph, px:px+pw]
                        person_features = cv2.resize(person_face, (100, 100))
                        
                        # Calculate histogram
                        person_hist = cv2.calcHist([person_features], [0], None, [256], [0, 256])
                        cv2.normalize(person_hist, person_hist)
                        
                        # Compare histograms
                        similarity = cv2.compareHist(target_hist, person_hist, cv2.HISTCMP_CORREL)
                        confidence = round(max(0, (similarity + 1) * 50), 2)
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = person
                            print(f"✅ Match found: {person['full_name']} - {confidence}%")
                else:
                    # Fallback to OpenCV method
                    is_match = detector.compare_faces(image_path, person_photo_path, threshold=70)
                    
                    if is_match:
                        face_detected_count += 1
                        print(f"✅ Potential match: {person['full_name']}")
                        # Only do detailed histogram if LBPH matches
                        person_img = cv2.imread(person_photo_path)
                        person_gray = cv2.cvtColor(person_img, cv2.COLOR_BGR2GRAY)
                        
                        # Detect face in person photo
                        person_faces = detector.face_cascade.detectMultiScale(
                            person_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                        )
                        
                        if len(person_faces) > 0:
                            px, py, pw, ph = person_faces[0]
                            person_face = person_gray[py:py+ph, px:px+pw]
                            person_features = cv2.resize(person_face, (100, 100))
                            
                            # Calculate histogram
                            person_hist = cv2.calcHist([person_features], [0], None, [256], [0, 256])
                            cv2.normalize(person_hist, person_hist)
                            
                            # Compare histograms (much faster now)
                            similarity = cv2.compareHist(target_hist, person_hist, cv2.HISTCMP_CORREL)
                            confidence = round(max(0, (similarity + 1) * 50), 2)
                            
                            if confidence > best_confidence:
                                best_confidence = confidence
                                best_match = person
                                print(f"✅ Match found: {person['full_name']} - {confidence}%")

            except Exception as e:
                print(f"⚠️ Error processing person {person['person_id']}: {e}")
                continue

        elapsed = time.time() - start_time
        print(f"\n⏱️ Scanning completed in {elapsed:.2f} seconds")
        print(f"📊 Total persons in DB: {len(persons)}")
        print(f"📊 Photos checked: {match_attempts}")
        print(f"📊 Faces detected in both: {face_detected_count}")
        print(f"📊 Best confidence: {best_confidence:.2f}%")
        print(f"📊 Match threshold: 45%\n")

        # ================= RESULT =================
        if best_match and best_confidence > 45:  # Lowered threshold for better matching
            result_data = {
                "status": "MATCH FOUND",
                "name": best_match["full_name"],
                "confidence": min(best_confidence, 98),
                "person_id": best_match["person_id"],
                "photo": best_match["photo_path"]
            }
            print(f"\n🎯 RETURNING RESULT: {result_data}\n")
            return result_data

        result_data = {"status": "NOT FOUND", "message": "No matching person found in database"}
        print(f"\n❌ RETURNING RESULT: {result_data}\n")
        return result_data

    except Exception as e:
        print(f"❌ Error in detect_image: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "status": "ERROR"}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.get("/auto-detect")
def auto_detect():
    try:
        import face_recognition
        import numpy as np

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ================= GET FRAMES =================
        cursor.execute("SELECT * FROM camera_frames ORDER BY id DESC LIMIT 10")
        frames = cursor.fetchall()

        # ================= GET MISSING PERSONS =================
        cursor.execute("SELECT * FROM missing_persons WHERE face_encoding IS NOT NULL")
        persons = cursor.fetchall()

        results = []

        for frame in frames:
            frame_path = os.path.join(UPLOAD_FOLDER, frame["image_path"])

            img = face_recognition.load_image_file(frame_path)
            encodings = face_recognition.face_encodings(img)

            if not encodings:
                continue

            input_encoding = encodings[0]

            best_match = None
            best_distance = 1.0

            # ================= MATCH =================
            for person in persons:
                try:
                    stored_encoding = np.array(eval(person["face_encoding"]))

                    distance = np.linalg.norm(stored_encoding - input_encoding)

                    if distance < best_distance:
                        best_distance = distance
                        best_match = person

                except:
                    continue

            # ================= RESULT =================
            if best_match and best_distance < 0.5:
                confidence = round((1 - best_distance) * 100, 2)

                results.append({
                    "frame": frame["image_path"],
                    "status": "MATCH FOUND",
                    "name": best_match["full_name"],
                    "confidence": confidence
                })

        return {
            "total_frames_checked": len(frames),
            "matches": results
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

# ================= ADVANCED FACE RECOGNITION (CNN-based) =================
@app.post("/recognize")
async def advanced_face_recognize(image: UploadFile = File(...)):
    """
    Advanced face recognition using CNN embeddings and Euclidean distance
    Returns match results with confidence scores and bounding boxes
    """
    try:
        import uuid
        import shutil
        from ai.advanced_face_recognition import recognize_face_in_image, AdvancedFaceRecognition
        
        # Generate unique filename
        file_ext = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(AI_IMAGES_FOLDER, file_name)
        
        # Save uploaded image
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        print(f"\n🔍 Processing image: {file_name}")
        
        # Perform face recognition
        results = recognize_face_in_image(file_path, use_cnn=False)  # Use HOG for speed
        
        # Draw bounding boxes on image
        output_filename = f"result_{file_name}"
        output_path = os.path.join(RECOGNIZED_FOLDER, output_filename)
        
        if results.get('matches'):
            recognizer = AdvancedFaceRecognition()
            recognizer.draw_face_boxes(file_path, results['matches'], output_path)
            results['annotated_image_url'] = f"http://127.0.0.1:8000/uploads/recognized/{output_filename}"
        
        results['original_image_url'] = f"http://127.0.0.1:8000/uploads/ai_images/{file_name}"
        
        return {
            "status": "success",
            "data": results
        }
        
    except Exception as e:
        print(f"❌ Recognition error: {e}")
        return {"error": str(e)}


# ================= ENCODE DATASET =================
@app.post("/encode-dataset")
def encode_missing_persons_dataset():
    """
    Encode all missing persons in dataset for fast recognition
    Call this endpoint when new persons are added to database
    """
    try:
        from ai.advanced_face_recognition import AdvancedFaceRecognition
        
        recognizer = AdvancedFaceRecognition()
        encodings = recognizer.encode_missing_persons()
        
        return {
            "status": "success",
            "message": f"Successfully encoded {len(encodings)} persons",
            "total_encoded": len(encodings)
        }
        
    except Exception as e:
        print(f"❌ Encoding error: {e}")
        return {"error": str(e)}

# ================= FEATURE 8: ANALYTICS DASHBOARD =================
@app.get("/api/analytics")
def get_analytics():
    """Get dashboard analytics and statistics"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Total cases
        cursor.execute("SELECT COUNT(*) as count FROM missing_persons")
        total_cases = cursor.fetchone()["count"]

        # Active cases (OPEN or IN_PROGRESS)
        cursor.execute("SELECT COUNT(*) as count FROM missing_persons WHERE status IN ('OPEN', 'IN_PROGRESS', 'MISSING')")
        active_cases = cursor.fetchone()["count"]

        # Solved cases (CLOSED or FOUND)
        cursor.execute("SELECT COUNT(*) as count FROM missing_persons WHERE status IN ('CLOSED', 'FOUND')")
        solved_cases = cursor.fetchone()["count"]

        # Total FIRs
        cursor.execute("SELECT COUNT(*) as count FROM fir_cases")
        total_firs = cursor.fetchone()["count"]

        # Total detections
        cursor.execute("SELECT COUNT(*) as count FROM detection_logs")
        total_detections = cursor.fetchone()["count"]

        # Recent matches (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) as count FROM detection_logs
            WHERE status = 'MATCH FOUND'
            AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        recent_matches = cursor.fetchone()["count"]

        # Pending/Unread alerts
        cursor.execute("SELECT COUNT(*) as count FROM detection_alerts WHERE is_read = 0")
        pending_alerts = cursor.fetchone()["count"]

        return {
            "total_cases": total_cases,
            "active_cases": active_cases,
            "solved_cases": solved_cases,
            "total_firs": total_firs,
            "total_detections": total_detections,
            "recent_matches": recent_matches,
            "matches_found": recent_matches,  # Add alias for frontend compatibility
            "pending_alerts": pending_alerts,  # Changed from unread_alerts
            "unread_alerts": pending_alerts  # Keep for backward compatibility
        }

    except Exception as e:
        print(f"❌ Analytics error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ================= FEATURE 9: DETECTION LOGS =================
@app.get("/api/detection-logs")
def get_detection_logs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM detection_logs
            ORDER BY created_at DESC
            LIMIT 100
        """)
        logs = cursor.fetchall()

        return {"data": logs}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


# ================= FEATURE 2: ALERT SYSTEM =================
class AlertRequest(BaseModel):
    person_id: int
    frame_id: int = None
    confidence: float
    alert_message: str

@app.post("/api/log-alert")
def log_alert(data: AlertRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO detection_alerts
            (person_id, frame_id, confidence, alert_message)
            VALUES (%s, %s, %s, %s)
        """, (data.person_id, data.frame_id, data.confidence, data.alert_message))

        conn.commit()
        return {"message": "Alert logged successfully", "alert_id": cursor.lastrowid}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

@app.get("/api/alerts")
def get_alerts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT a.*, m.full_name as person_name
            FROM detection_alerts a
            LEFT JOIN missing_persons m ON a.person_id = m.person_id
            ORDER BY a.created_at DESC
            LIMIT 50
        """)
        alerts = cursor.fetchall()

        return {"data": alerts}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

@app.put("/api/alert/{alert_id}/read")
def mark_alert_read(alert_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE detection_alerts
            SET is_read = 1
            WHERE alert_id = %s
        """, (alert_id,))

        conn.commit()
        return {"message": "Alert marked as read"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


# ================= FEATURE 5: VIDEO FACE DETECTION =================
# @app.post("/api/detect-video")
# async def detect_video(file: UploadFile = File(...)):
#     try:
#         import face_recognition
#
#         # Save video
#         video_path = os.path.join(UPLOAD_FOLDER, file.filename)
#         with open(video_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#
#         # Extract frames and detect faces
#         cap = cv2.VideoCapture(video_path)
#         results = []
#         frame_count = 0
#         fps = cap.get(cv2.CAP_PROP_FPS)
#         frame_interval = int(fps * 2)  # Every 2 seconds
#
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
#
#             frame_count += 1
#
#             # Process every N frames
#             if frame_count % frame_interval == 0:
#                 # Convert to RGB
#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#
#                 # Detect faces
#                 face_locations = face_recognition.face_locations(rgb_frame)
#
#                 if face_locations:
#                     timestamp = frame_count / fps
#                     results.append({
#                         "timestamp": round(timestamp, 2),
#                         "frame_number": frame_count,
#                         "face_count": len(face_locations),
#                         "locations": face_locations
#                     })
#
#         cap.release()
#
#         return {
#             "video": file.filename,
#             "total_frames": frame_count,
#             "faces_detected": len(results),
#             "results": results
#         }
#
#     except Exception as e:
#         return {"error": str(e)}


# ================= FEATURE 6: MULTI-FACE DETECTION =================
# @app.post("/api/detect-faces")
# async def detect_faces(file: UploadFile = File(...)):
#     try:
#         import face_recognition
#
#         # Save image
#         image_path = os.path.join(UPLOAD_FOLDER, file.filename)
#         with open(image_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#
#         # Load image
#         image = face_recognition.load_image_file(image_path)
#
#         # Find all faces
#         face_locations = face_recognition.face_locations(image)
#         face_encodings = face_recognition.face_encodings(image, face_locations)
#
#         faces = []
#         for i, (top, right, bottom, left) in enumerate(face_locations):
#             faces.append({
#                 "face_number": i + 1,
#                 "location": {
#                     "top": top,
#                     "right": right,
#                     "bottom": bottom,
#                     "left": left
#                 },
#                 "has_encoding": i < len(face_encodings)
#             })
#
#         return {
#             "image": file.filename,
#             "total_faces": len(faces),
#             "faces": faces
#         }
#
#     except Exception as e:
#         return {"error": str(e)}
