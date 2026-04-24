from database import get_db_connection
from auth.password_utils import hash_password, verify_password
from auth.jwt_utils import create_access_token


# ================= REGISTER =================
def register_user(full_name, email, password, role_name, station_id=None):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        password_hash = hash_password(password)

        query = """
        INSERT INTO users (full_name, email, password_hash, role_name, station_id)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (full_name, email, password_hash, role_name, station_id))
        conn.commit()

        return True

    except Exception as e:
        print("❌ REGISTER ERROR:", e)
        return False

    finally:
        cursor.close()
        conn.close()


# ================= LOGIN =================
def login_user(email: str, password: str):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT user_id, email, password_hash, role_name, station_id
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cursor.fetchone()

        # ❌ user not found
        if not user:
            return None

        # ❌ wrong password
        if not verify_password(password, user["password_hash"]):
            return None

        # ================= ROLE MAPPING =================
        # 🔥 Match with your roles table
        role_map = {
            "Admin": 1,
            "Police": 2,
            "User": 3,
            "admin": 1,
            "police": 2,
            "citizen": 3,
            "user": 3
        }

        role_id = role_map.get(user["role_name"], 3)

        # ================= TOKEN DATA =================
        token_data = {
            "user_id": user["user_id"],
            "email": user["email"],
            "role": user["role_name"],   # optional
            "role_id": role_id,          # 🔥 IMPORTANT
            "station_id": user["station_id"]
        }

        access_token = create_access_token(token_data)

        return access_token

    except Exception as e:
        print("❌ LOGIN ERROR:", e)
        return None

    finally:
        cursor.close()
        conn.close()
