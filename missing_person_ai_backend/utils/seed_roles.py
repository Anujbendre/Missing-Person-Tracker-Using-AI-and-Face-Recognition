from database import get_db_connection

roles = [
    "SUPER_ADMIN",
    "SYSTEM_ADMIN",
    "POLICE_OFFICER",
    "INVESTIGATING_OFFICER",
    "PUBLIC_REPORTER",
    "CCTV_OPERATOR",
    "AI_MODEL_MANAGER",
    "DATA_ANALYST",
    "FORENSIC_OFFICER",
    "SECURITY_OFFICER"
]

conn = get_db_connection()
cursor = conn.cursor()

for role in roles:
    cursor.execute(
        "INSERT IGNORE INTO roles (role_name) VALUES (%s)",
        (role,)
    )

conn.commit()
cursor.close()
conn.close()

print("✅ Roles inserted successfully")
