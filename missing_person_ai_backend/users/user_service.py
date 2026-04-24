from database import get_db_connection
from fastapi import HTTPException


def create_missing_person_case(data, reported_by, photo_path):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO missing_persons
        (full_name, age, gender, last_seen_location, last_seen_date, photo_path, reported_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                data.full_name,
                data.age,
                data.gender,
                data.last_seen_location,
                data.last_seen_date,
                photo_path,
                reported_by
            )
        )

        person_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO alerts (sent_to, alert_status) VALUES (%s, %s)",
            (reported_by, "CASE_CREATED")
        )

        conn.commit()
        return person_id

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()