from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from auth.auth_dependency import require_permission, get_current_user
from cases.case_service import create_fir_case
from utils.pdf_generator import generate_fir_pdf
from utils.fir_schema import FIRCreateSchema
from database import get_db_connection
import os

router = APIRouter(prefix="/users", tags=["FIR"])


# ================= APPLY FIR =================

@router.post("/apply-fir")
def apply_fir(
    data: FIRCreateSchema,
    user=Depends(require_permission("create_case"))
):
    case_id, case_number = create_fir_case(
        person_id=data.person_id,
        user_id=user["user_id"],
        priority=data.priority
    )

    return {
        "message": "FIR registered successfully",
        "case_id": case_id,
        "case_number": case_number
    }


# ================= DOWNLOAD FIR =================

@router.get("/fir/{case_id}/download")
def download_fir(
    case_id: int,
    user=Depends(require_permission("view_cases"))
):
    file_name = f"fir_{case_id}.pdf"

    generate_fir_pdf(case_id, file_name)

    return FileResponse(
        path=file_name,
        media_type="application/pdf",
        filename=file_name
    )


# ================= VIEW CASES BASED ON ROLE =================

@router.get("/cases")
def get_cases(user=Depends(get_current_user)):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if user["role"] == "Admin":
        cursor.execute("SELECT * FROM cases")

    elif user["role"] == "Police":
        cursor.execute(
            "SELECT * FROM cases WHERE station_id=%s",
            (user["station_id"],)
        )

    else:
        cursor.execute(
            "SELECT * FROM missing_persons"
        )

    return cursor.fetchall()

# ==============================
# Update Case Status
# ==============================

@router.put("/cases/{case_id}/status")
def update_case_status(case_id: int, status: str):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE cases SET case_status=%s WHERE case_id=%s",
        (status, case_id)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Case updated"}

# ==============================
# Assign Police Officer
# ==============================

@router.put("/cases/{case_id}/assign")
def assign_officer(case_id: int, officer_id: int):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE cases SET assigned_officer=%s WHERE case_id=%s",
        (officer_id, case_id)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Officer assigned"}
