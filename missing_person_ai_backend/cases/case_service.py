from database import get_db_connection
import random
import datetime


# ================= GENERATE CASE NUMBER =================
def generate_case_number():
    year = datetime.datetime.now().year
    random_number = random.randint(1000, 9999)
    return f"FIR-{year}-{random_number}"


# ================= CREATE FIR CASE =================
def create_fir_case(person_id, station_id, priority):

    conn = get_db_connection()
    cursor = conn.cursor()

    case_number = generate_case_number()

    query = """
    INSERT INTO cases (person_id, station_id, priority, case_number)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (person_id, station_id, priority, case_number))

    conn.commit()

    case_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return case_id, case_number
