# ================= FEATURE 8: ANALYTICS DASHBOARD =================
@app.get("/api/analytics")
def get_analytics():
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

        # Unread alerts
        cursor.execute("SELECT COUNT(*) as count FROM detection_alerts WHERE is_read = 0")
        unread_alerts = cursor.fetchone()["count"]

        return {
            "total_cases": total_cases,
            "active_cases": active_cases,
            "solved_cases": solved_cases,
            "total_firs": total_firs,
            "total_detections": total_detections,
            "recent_matches": recent_matches,
            "unread_alerts": unread_alerts
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
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
@app.post("/api/detect-video")
async def detect_video(file: UploadFile = File(...)):
    try:
        import face_recognition

        # Save video
        video_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract frames and detect faces
        cap = cv2.VideoCapture(video_path)
        results = []
        frame_count = 0
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * 2)  # Every 2 seconds

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Process every N frames
            if frame_count % frame_interval == 0:
                # Convert to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                face_locations = face_recognition.face_locations(rgb_frame)
                
                if face_locations:
                    timestamp = frame_count / fps
                    results.append({
                        "timestamp": round(timestamp, 2),
                        "frame_number": frame_count,
                        "face_count": len(face_locations),
                        "locations": face_locations
                    })

        cap.release()

        return {
            "video": file.filename,
            "total_frames": frame_count,
            "faces_detected": len(results),
            "results": results
        }

    except Exception as e:
        return {"error": str(e)}


# ================= FEATURE 6: MULTI-FACE DETECTION =================
@app.post("/api/detect-faces")
async def detect_faces(file: UploadFile = File(...)):
    try:
        import face_recognition

        # Save image
        image_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load image
        image = face_recognition.load_image_file(image_path)
        
        # Find all faces
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        faces = []
        for i, (top, right, bottom, left) in enumerate(face_locations):
            faces.append({
                "face_number": i + 1,
                "location": {
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left
                },
                "has_encoding": i < len(face_encodings)
            })

        return {
            "image": file.filename,
            "total_faces": len(faces),
            "faces": faces
        }

    except Exception as e:
        return {"error": str(e)}
