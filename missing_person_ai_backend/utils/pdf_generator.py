from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from database import get_db_connection

def generate_fir_pdf(case_id: int, file_path: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            c.case_number,
            c.case_status,
            c.priority,
            c.created_at,
            m.full_name AS missing_name,
            m.age,
            m.gender,
            m.last_seen_location,
            m.last_seen_date,
            u.full_name AS reporter_name
        FROM cases c
        JOIN missing_persons m ON c.person_id = m.person_id
        JOIN users u ON m.reported_by = u.user_id
        WHERE c.case_id = %s
        """,
        (case_id,)
    )

    data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not data:
        raise Exception("Invalid case ID")

    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("Helvetica", 11)

    y = 800
    c.drawString(50, y, "FIR COPY – Missing Person Case")
    y -= 30

    c.drawString(50, y, f"FIR Number: {data['case_number']}")
    y -= 20
    c.drawString(50, y, f"Reporter Name: {data['reporter_name']}")
    y -= 20
    c.drawString(50, y, f"Missing Person Name: {data['missing_name']}")
    y -= 20
    c.drawString(50, y, f"Age: {data['age']} | Gender: {data['gender']}")
    y -= 20
    c.drawString(50, y, f"Last Seen Location: {data['last_seen_location']}")
    y -= 20
    c.drawString(50, y, f"Last Seen Date: {data['last_seen_date']}")
    y -= 20
    c.drawString(50, y, f"Case Status: {data['case_status']}")
    y -= 20
    c.drawString(50, y, f"Priority: {data['priority']}")

    y -= 40
    c.drawString(50, y, "This FIR is system generated and valid for official use.")

    c.showPage()
    c.save()
