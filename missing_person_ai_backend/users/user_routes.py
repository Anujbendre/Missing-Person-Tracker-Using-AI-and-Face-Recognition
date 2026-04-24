import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from database import get_db_connection
from schemas.user_case_schema import MissingPersonCase
from users.user_service import create_missing_person_case
from auth.auth_dependency import require_permission, require_role

router = APIRouter(prefix="/user", tags=["User Module"])

# Upload folder
UPLOAD_DIR = "uploads/missing_persons"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed image types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


# ==============================
# Validate File Name
# ==============================

def get_safe_filename(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}"
        )

    return f"{uuid.uuid4()}{ext}"


# ==============================
# REPORT MISSING PERSON
# ==============================

@router.post("/report-missing")
async def report_missing(
    name: str,
    age: int,
    image: UploadFile = File(...),
    user=Depends(require_role("User"))
):

    file_path = f"uploads/{uuid.uuid4()}.jpg"

    with open(file_path, "wb") as f:
        f.write(await image.read())

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO missing_persons (name, age, photo_path)
        VALUES (%s, %s, %s)
    """, (name, age, file_path))

    conn.commit()

    return {"message": "Missing person added"}
# ==============================
# GET ALL MISSING PERSONS
# ==============================

@router.get("/missing-persons")
def get_all_missing_persons():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM missing_persons ORDER BY created_at DESC")

    persons = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total": len(persons),
        "data": persons
    }


# ==============================
# SEARCH MISSING PERSON
# ==============================

@router.get("/search")
def search_missing_person(name: str):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT * FROM missing_persons
    WHERE full_name LIKE %s
    """

    cursor.execute(query, (f"%{name}%",))

    persons = cursor.fetchall()

    cursor.close()
    conn.close()

    return persons
