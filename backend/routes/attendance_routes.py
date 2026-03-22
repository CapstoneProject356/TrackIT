from flask import Blueprint, request, jsonify, render_template
from backend.models.attendance import Attendance
from backend.models.qr_session import QRSession
from backend.database.db_init import db
from backend.utils.gps_checker import verify_gps
from backend.utils.face_recognition import verify_face
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from sqlalchemy import extract
from collections import defaultdict
from backend.models.user import User

# Blueprint
attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")
@login_required


# =========================================================
# VERIFY & MARK ATTENDANCE
# =========================================================

def verify_and_mark_attendance(student_id, session_id, face_image, latitude, longitude):

    # ---------- Check QR Session ----------
    qr_session = QRSession.query.get(session_id)

    if not qr_session:
        return {"error": "Invalid session"}

    if not qr_session.active:
        return {"error": "Session expired"}

    if datetime.utcnow() > qr_session.expires_at:
        qr_session.active = False
        db.session.commit()
        return {"error": "QR code expired"}


    # ---------- Prevent Duplicate Attendance ----------
    existing = Attendance.query.filter_by(
        student_id=student_id,
        session_id=session_id
    ).first()

    if existing:
        return {"error": "Attendance already marked"}


    # ---------- GPS Verification ----------
    if not verify_gps(latitude, longitude):
        return {"error": "You are not inside the classroom"}


    # ---------- Face Already Verified ----------
    # Face verification is handled in /face/verify


    # ---------- Read Face Image ----------
    image_bytes = None
    if face_image:
        image_bytes = face_image.read()


    # ---------- Save Attendance ----------
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
# MARK ATTENDANCE ROUTE
# =========================================================

@attendance_bp.route("/mark", methods=["POST"])
def mark_attendance():

    student_id = request.form.get("student_id")
    session_id = request.form.get("session_id")

    latitude = float(request.form.get("latitude"))
    longitude = float(request.form.get("longitude"))

    face_image = request.files.get("face_image")

    # ---------- Validate Input ----------
    if not student_id or not session_id or not face_image:
        return jsonify({"error": "Missing required data"}), 400


    result = verify_and_mark_attendance(
        student_id,
        session_id,
        face_image,
        latitude,
        longitude
    )

    return jsonify(result)


# =========================================================
# DAILY REPORT
# =========================================================
@attendance_bp.route("/daily_report")
def daily_report():
    today = datetime.utcnow().date()
    if current_user.role == "student":
        students = [current_user]  # only self
    else:
        students = User.query.filter_by(role="student").all()  # all students

    # get today's attendance
    records_dict = {a.student_id: a for a in Attendance.query.filter(db.func.date(Attendance.timestamp) == today).all()}

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
# WEEKLY REPORT
# =========================================================

@attendance_bp.route("/weekly_report")
def weekly_report():
    # fetch all attendance
    if current_user.role == "student":
        records = Attendance.query.filter(Attendance.student_id == current_user.id).order_by(Attendance.timestamp).all()
        students = [current_user]
    else:
        records = Attendance.query.order_by(Attendance.timestamp).all()
        students = User.query.filter_by(role="student").all()

    # sequential weeks based on lecture dates
    unique_weeks = sorted({r.timestamp.date() for r in records})
    date_to_week = {date: idx+1 for idx, date in enumerate(unique_weeks)}

    student_weeks = defaultdict(lambda: defaultdict(lambda: {"present": 0, "total": 0}))
    for r in records:
        week_num = date_to_week[r.timestamp.date()]
        student_weeks[r.student.name][week_num]["total"] += 1
        if r.face_verified:
            student_weeks[r.student.name][week_num]["present"] += 1

    summary = []
    for student in students:
        for week_num in range(1, len(unique_weeks)+1):
            data = student_weeks[student.name].get(week_num, {"present": 0, "total": 1})
            percent = round((data["present"]/data["total"])*100, 2) if data["total"] else 0
            summary.append({
                "name": student.name,
                "week": f"Week {week_num}",
                "percentage": percent
            })

    return render_template("weekly_report.html", records=summary)
# =========================================================
# MONTHLY REPORT
# =========================================================
@attendance_bp.route("/monthly_report")
def monthly_report():
    if current_user.role == "student":
        records = Attendance.query.filter(Attendance.student_id == current_user.id).all()
        students = [current_user]
    else:
        records = Attendance.query.all()
        students = User.query.filter_by(role="student").all()

    student_months = defaultdict(lambda: defaultdict(lambda: {"present": 0, "total": 0}))
    for r in records:
        month = r.timestamp.month
        student_months[r.student.name][month]["total"] += 1
        if r.face_verified:
            student_months[r.student.name][month]["present"] += 1

    months_with_lectures = sorted({r.timestamp.month for r in records})
    month_names = ["January","February","March","April","May","June","July","August","September","October","November","December"]

    summary = []
    for student in students:
        for m in months_with_lectures:
            data = student_months[student.name].get(m, {"present": 0, "total": 1})
            percent = round((data["present"]/data["total"])*100, 2) if data["total"] else 0
            summary.append({
                "name": student.name,
                "month": month_names[m-1],
                "percentage": percent
            })

    return render_template("monthly_report.html", records=summary)

# =========================================================
# YEARLY REPORT
# =========================================================
@attendance_bp.route("/yearly_report")
def yearly_report():
    today = datetime.utcnow().date()
    
    # Determine academic year: July - June
    if today.month >= 7:  # July or later
        start_year = today.year
        end_year = today.year + 1
    else:  # Jan - June
        start_year = today.year - 1
        end_year = today.year

    academic_year = f"{start_year}-{end_year}"

    if current_user.role == "student":
        students = [current_user]
        records = Attendance.query.filter(
            Attendance.student_id == current_user.id,
            extract('year', Attendance.timestamp) >= start_year,
            extract('year', Attendance.timestamp) <= end_year
        ).all()
    else:
        students = User.query.filter_by(role="student").all()
        records = Attendance.query.filter(
            extract('year', Attendance.timestamp) >= start_year,
            extract('year', Attendance.timestamp) <= end_year
        ).all()

    # Calculate attendance %
    student_data = {}
    for student in students:
        student_records = [r for r in records if r.student_id == student.id]
        total = len(student_records)
        present = sum(1 for r in student_records if r.face_verified)
        percentage = round((present / total) * 100, 2) if total else 0
        student_data[student.name] = {
            "academic_year": academic_year,
            "percentage": percentage
        }

    summary = []
    for name, data in student_data.items():
        summary.append({
            "name": name,
            "academic_year": data["academic_year"],
            "percentage": data["percentage"]
        })

    return render_template("yearly_report.html", records=summary)