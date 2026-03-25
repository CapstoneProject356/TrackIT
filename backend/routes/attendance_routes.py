from flask import Blueprint, request, jsonify, render_template, send_file
from backend.models.attendance import Attendance
from backend.models.qr_session import QRSession
from backend.database.db_init import db
from backend.utils.gps_checker import verify_gps
from backend.utils.face_recognition import verify_face
from datetime import datetime
from flask_login import login_required, current_user
from sqlalchemy import extract
from collections import defaultdict
from backend.models.user import User
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import io


# =========================================================
# PDF GENERATOR
# =========================================================
def generate_pdf(title, headers, data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles['Title']))

    table_data = [headers] + data

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return buffer


# Blueprint
attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


# =========================================================
# VERIFY & MARK ATTENDANCE
# =========================================================
def verify_and_mark_attendance(student_id, session_id, face_image, latitude, longitude):

    qr_session = QRSession.query.get(session_id)

    if not qr_session:
        return {"error": "Invalid session"}

    if not qr_session.active:
        return {"error": "Session expired"}

    if datetime.utcnow() > qr_session.expires_at:
        qr_session.active = False
        db.session.commit()
        return {"error": "QR code expired"}

    existing = Attendance.query.filter_by(
        student_id=student_id,
        session_id=session_id
    ).first()

    if existing:
        return {"error": "Attendance already marked"}

    if not verify_gps(latitude, longitude):
        return {"error": "You are not inside the classroom"}

    image_bytes = face_image.read() if face_image else None

    attendance = Attendance(
        student_id=student_id,
        session_id=session_id,
        gps_lat=latitude,
        gps_long=longitude,
        qr_token=qr_session.token,
        face_verified=True,
        timestamp=datetime.utcnow(),
        face_image=image_bytes
    )

    db.session.add(attendance)
    db.session.commit()

    return {"success": "Attendance marked successfully"}


# =========================================================
# MARK ATTENDANCE
# =========================================================
@attendance_bp.route("/mark", methods=["POST"])
def mark_attendance():

    student_id = request.form.get("student_id")
    session_id = request.form.get("session_id")

    latitude = float(request.form.get("latitude"))
    longitude = float(request.form.get("longitude"))

    face_image = request.files.get("face_image")

    if not student_id or not session_id or not face_image:
        return jsonify({"error": "Missing required data"}), 400

    result = verify_and_mark_attendance(
        student_id, session_id, face_image, latitude, longitude
    )

    return jsonify(result)


# =========================================================
# DAILY REPORT (HTML)
# =========================================================
@attendance_bp.route("/daily_report")
@login_required
def daily_report():
    today = datetime.utcnow().date()

    students = [current_user] if current_user.role == "student" \
        else User.query.filter_by(role="student").all()

    records_dict = {
        a.student_id: a for a in Attendance.query.filter(
            db.func.date(Attendance.timestamp) == today
        ).all()
    }

    summary = []
    for student in students:
        attendance = records_dict.get(student.id)
        summary.append({
            "name": student.name,
            "date": today.strftime("%Y-%m-%d"),
            "status": "Present" if attendance and attendance.face_verified else "Absent"
        })

    return render_template("daily_report.html", records=summary)


# =========================================================
# DAILY PDF
# =========================================================
@attendance_bp.route("/daily_report/pdf")
@login_required
def daily_report_pdf():
    today = datetime.utcnow().date()

    students = [current_user] if current_user.role == "student" \
        else User.query.filter_by(role="student").all()

    records_dict = {
        a.student_id: a for a in Attendance.query.filter(
            db.func.date(Attendance.timestamp) == today
        ).all()
    }

    data = []
    for student in students:
        attendance = records_dict.get(student.id)
        status = "Present" if attendance and attendance.face_verified else "Absent"

        data.append([student.name, today.strftime("%Y-%m-%d"), status])

    pdf = generate_pdf("Daily Report", ["Name", "Date", "Status"], data)

    return send_file(pdf, download_name="daily_report.pdf", as_attachment=True)


# =========================================================
# WEEKLY REPORT (HTML)
# =========================================================
@attendance_bp.route("/weekly_report")
@login_required
def weekly_report():

    if current_user.role == "student":
        records = Attendance.query.filter_by(student_id=current_user.id).all()
        students = [current_user]
    else:
        records = Attendance.query.all()
        students = User.query.filter_by(role="student").all()

    unique_weeks = sorted({r.timestamp.date() for r in records})
    date_to_week = {d: i+1 for i, d in enumerate(unique_weeks)}

    student_weeks = defaultdict(lambda: defaultdict(lambda: {"present": 0, "total": 0}))

    for r in records:
        w = date_to_week[r.timestamp.date()]
        student_weeks[r.student.name][w]["total"] += 1
        if r.face_verified:
            student_weeks[r.student.name][w]["present"] += 1

    summary = []
    for student in students:
        for w in range(1, len(unique_weeks)+1):
            d = student_weeks[student.name].get(w, {"present": 0, "total": 1})
            percent = round((d["present"]/d["total"])*100, 2)
            summary.append({
                "name": student.name,
                "week": f"Week {w}",
                "percentage": percent
            })

    return render_template("weekly_report.html", records=summary)


# =========================================================
# WEEKLY PDF
# =========================================================
@attendance_bp.route("/weekly_report/pdf")
@login_required
def weekly_report_pdf():

    if current_user.role == "student":
        records = Attendance.query.filter_by(student_id=current_user.id).all()
        students = [current_user]
    else:
        records = Attendance.query.all()
        students = User.query.filter_by(role="student").all()

    unique_weeks = sorted({r.timestamp.date() for r in records})
    date_to_week = {d: i+1 for i, d in enumerate(unique_weeks)}

    student_weeks = defaultdict(lambda: defaultdict(lambda: {"present": 0, "total": 0}))

    for r in records:
        w = date_to_week[r.timestamp.date()]
        student_weeks[r.student.name][w]["total"] += 1
        if r.face_verified:
            student_weeks[r.student.name][w]["present"] += 1

    data = []
    for student in students:
        for w in range(1, len(unique_weeks)+1):
            d = student_weeks[student.name].get(w, {"present": 0, "total": 1})
            percent = round((d["present"]/d["total"])*100, 2)

            data.append([student.name, f"Week {w}", f"{percent}%"])

    pdf = generate_pdf("Weekly Report", ["Name", "Week", "Attendance %"], data)

    return send_file(pdf, download_name="weekly_report.pdf", as_attachment=True)


# =========================================================
# MONTHLY REPORT (HTML)
# =========================================================
@attendance_bp.route("/monthly_report")
@login_required
def monthly_report():

    if current_user.role == "student":
        records = Attendance.query.filter_by(student_id=current_user.id).all()
        students = [current_user]
    else:
        records = Attendance.query.all()
        students = User.query.filter_by(role="student").all()

    student_months = defaultdict(lambda: defaultdict(lambda: {"present": 0, "total": 0}))

    for r in records:
        m = r.timestamp.month
        student_months[r.student.name][m]["total"] += 1
        if r.face_verified:
            student_months[r.student.name][m]["present"] += 1

    months = sorted({r.timestamp.month for r in records})
    names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    summary = []
    for student in students:
        for m in months:
            d = student_months[student.name].get(m, {"present": 0, "total": 1})
            percent = round((d["present"]/d["total"])*100, 2)

            summary.append({
                "name": student.name,
                "month": names[m-1],
                "percentage": percent
            })

    return render_template("monthly_report.html", records=summary)


# =========================================================
# MONTHLY PDF
# =========================================================
@attendance_bp.route("/monthly_report/pdf")
@login_required
def monthly_report_pdf():

    if current_user.role == "student":
        records = Attendance.query.filter_by(student_id=current_user.id).all()
        students = [current_user]
    else:
        records = Attendance.query.all()
        students = User.query.filter_by(role="student").all()

    student_months = defaultdict(lambda: defaultdict(lambda: {"present": 0, "total": 0}))

    for r in records:
        m = r.timestamp.month
        student_months[r.student.name][m]["total"] += 1
        if r.face_verified:
            student_months[r.student.name][m]["present"] += 1

    months = sorted({r.timestamp.month for r in records})
    names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    data = []
    for student in students:
        for m in months:
            d = student_months[student.name].get(m, {"present": 0, "total": 1})
            percent = round((d["present"]/d["total"])*100, 2)

            data.append([student.name, names[m-1], f"{percent}%"])

    pdf = generate_pdf("Monthly Report", ["Name", "Month", "Attendance %"], data)

    return send_file(pdf, download_name="monthly_report.pdf", as_attachment=True)


# =========================================================
# YEARLY REPORT (NOW = DATE RANGE AVERAGE REPORT)
# =========================================================
@attendance_bp.route("/yearly_report", methods=["GET", "POST"])
def yearly_report():

    if request.method == "POST":

        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        # Convert to datetime
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Get records in date range
        if current_user.role == "student":
            students = [current_user]
            records = Attendance.query.filter(
                Attendance.student_id == current_user.id,
                Attendance.timestamp >= start_date,
                Attendance.timestamp <= end_date
            ).all()
        else:
            students = User.query.filter_by(role="student").all()
            records = Attendance.query.filter(
                Attendance.timestamp >= start_date,
                Attendance.timestamp <= end_date
            ).all()

        # Prepare summary
        summary = []

        for student in students:
            student_records = [r for r in records if r.student_id == student.id]

            total = len(student_records)
            present = sum(1 for r in student_records if r.face_verified)

            percentage = round((present / total) * 100, 2) if total else 0

            summary.append({
                "name": student.name,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "percentage": percentage
            })

        return render_template("yearly_report.html", records=summary)

    # First load
    return render_template("yearly_report.html", records=None)
# =========================================================
# PDF DOWNLOAD FOR AVERAGE REPORT
# =========================================================
@attendance_bp.route("/yearly_report/pdf", methods=["POST"])
def yearly_report_pdf():

    start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
    end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")

    if current_user.role == "student":
        students = [current_user]
        records = Attendance.query.filter(
            Attendance.student_id == current_user.id,
            Attendance.timestamp >= start_date,
            Attendance.timestamp <= end_date
        ).all()
    else:
        students = User.query.filter_by(role="student").all()
        records = Attendance.query.filter(
            Attendance.timestamp >= start_date,
            Attendance.timestamp <= end_date
        ).all()

    # IMPORTANT: Use LIST (not dict)
    data = []

    for student in students:
        student_records = [r for r in records if r.student_id == student.id]

        total = len(student_records)
        present = sum(1 for r in student_records if r.face_verified)

        percent = round((present / total) * 100, 2) if total else 0

        data.append([
            student.name,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            f"{percent}%"
        ])

    pdf = generate_pdf(
        "Attendance Report",
        ["Name", "From", "To", "Attendance %"],
        data
    )

    return send_file(pdf, download_name="attendance_report.pdf", as_attachment=True)