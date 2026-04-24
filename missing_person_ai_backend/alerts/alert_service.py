from database import get_db_connection


def create_alert(match_id, police_user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO alerts (match_id, sent_to, alert_status)
    VALUES (%s, %s, 'pending')
    """

    cursor.execute(query, (match_id, police_user_id))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Alert created successfully"}
