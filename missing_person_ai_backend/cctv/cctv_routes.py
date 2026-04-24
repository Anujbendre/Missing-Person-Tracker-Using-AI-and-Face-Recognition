from fastapi import APIRouter
from fastapi.params import Depends

from auth.auth_dependency import require_role
from cctv.cctv_service import add_camera, get_cameras
from database import get_db_connection

router = APIRouter(
    prefix="/cctv",
    tags=["CCTV Module"]
)


# =============================
# ADD CCTV CAMERA
# =============================

@router.post("/add-camera")
def add_camera(location: str, stream_url: str,
               user=Depends(require_role("Police"))):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cctv_cameras (location, stream_url, station_id, status)
        VALUES (%s, %s, %s, 'active')
    """, (location, stream_url, user["station_id"]))

    conn.commit()

    return {"message": "Camera added"}

# =============================
# GET ALL CAMERAS
# =============================

@router.get("/cameras")
def get_all_cameras():

    cameras = get_cameras()

    return cameras
