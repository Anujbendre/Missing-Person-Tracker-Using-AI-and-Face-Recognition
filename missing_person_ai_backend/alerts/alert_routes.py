from fastapi import APIRouter
from database import get_db_connection

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)

@router.get("/all")
def get_alerts():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT a.alert_id, a.alert_status, a.sent_at,
           m.person_id, m.camera_id, m.confidence
    FROM alerts a
    JOIN match_logs m ON a.match_id = m.match_id
    """

    cursor.execute(query)

    alerts = cursor.fetchall()

    cursor.close()
    conn.close()

    return alerts
