from database import get_db_connection


# ================= USERS =================

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT user_id, full_name, email, role_id, is_active, created_at FROM users")
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return users


def change_user_role(user_id: int, role_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET role_id=%s WHERE user_id=%s",
        (role_id, user_id)
    )

    conn.commit()
    cursor.close()
    conn.close()


def delete_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))

    conn.commit()
    cursor.close()
    conn.close()


# ================= CASES =================

def get_all_cases():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM cases")
    cases = cursor.fetchall()

    cursor.close()
    conn.close()

    return cases


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


# ================= DASHBOARD =================

def dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    users = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as total_cases FROM cases")
    cases = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "total_users": users["total_users"],
        "total_cases": cases["total_cases"]
    }
