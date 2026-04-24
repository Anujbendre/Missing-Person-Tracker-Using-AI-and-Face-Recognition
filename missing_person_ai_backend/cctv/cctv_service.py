from database import get_db_connection


# =============================
# ADD CAMERA
# =============================

def add_camera(location, stream_url):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO cctv_cameras (location, stream_url, status)
    VALUES (%s, %s, 'active')
    """

    cursor.execute(query, (location, stream_url))
    conn.commit()

    camera_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return camera_id


# =============================
# GET ALL CAMERAS
# =============================

def get_cameras():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM cctv_cameras")

    cameras = cursor.fetchall()

    cursor.close()
    conn.close()

    return cameras
