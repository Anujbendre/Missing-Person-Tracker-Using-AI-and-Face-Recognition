import cv2
import time
import os
import mysql.connector

# 👉 Your camera URL
url = "http://192.168.1.5:8080/video"

camera_id = 1  # from DB

os.makedirs("frames", exist_ok=True)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="missing_person_ai"
)

cursor = db.cursor()

cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    filename = f"frames/frame_{int(time.time())}.jpg"
    cv2.imwrite(filename, frame)

    # 👉 Insert into YOUR table
    sql = "INSERT INTO cctv_footage (camera_id, file_path) VALUES (%s, %s)"
    cursor.execute(sql, (camera_id, filename))
    db.commit()

    print("Saved:", filename)

    time.sleep(2)
