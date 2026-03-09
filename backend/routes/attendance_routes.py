from flask import Blueprint, request, jsonify, render_template, session
from backend.models.attendance import Attendance
from backend.models.qr_session import QRSession
from backend.database.db_init import db
from backend.utils.gps_checker import verify_gps
from backend.utils.face_recognition import verify_face
from datetime import datetime, timedelta

# Blueprint with prefix
attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


# ---------------- VERIFY & MARK ATTENDANCE ---------------- #

def verify_and_mark_attendance(student_id, session_id, face_image, latitude, longitude):

    # Check session
    session = QRSession.query.get(session_id)

    if not session:
        return {"error": "Invalid session"}

    if not session.active:
        return {"error": "Session expired"}

    # Check expiry
    if datetime.utcnow() > session.expires_at:
        session.active = False
        db.session.commit()
        return {"error": "QR code expired"}

    # Prevent duplicate attendance
    existing = Attendance.query.filter_by(
        student_id=student_id,
        session_id=session_id
    ).first()

    if existing:
        return {"error": "Attendance already marked"}

    # GPS Verification
    if not verify_gps(latitude, longitude):
        return {"error": "You are not inside the classroom"}

    # Face Verification
    if not verify_face(student_id, face_image):
        return {"error": "Face verification failed"}

    # Save attendance
    attendance = Attendance(
        student_id=student_id,
        session_id=session_id,
        gps_lat=latitude,
        gps_long=longitude,
        face_verified=True,
        timestamp=datetime.utcnow()
    )

    db.session.add(attendance)
    db.session.commit()

    return {"success": "Attendance marked successfully"}


# ---------------- MARK ATTENDANCE ROUTE ---------------- #

@attendance_bp.route("/mark", methods=["POST"])
def mark_attendance():

    student_id = request.form.get("student_id")
    session_id = request.form.get("session_id")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    face_image = request.files.get("face_image")

    # Validate input
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


# ---------------- DAILY REPORT ---------------- #

@attendance_bp.route("/daily_report")
def daily_report():

    today = datetime.utcnow().date()

    records = Attendance.query.filter(
        db.func.date(Attendance.timestamp) == today
    ).all()

    return render_template(
        "daily_report.html",
        records=records
    )


# ---------------- WEEKLY REPORT ---------------- #

@attendance_bp.route("/weekly_report")
def weekly_report():

    week_ago = datetime.utcnow() - timedelta(days=7)

    records = Attendance.query.filter(
        Attendance.timestamp >= week_ago
    ).all()

    return render_template(
        "weekly_report.html",
        records=records
    )


# ---------------- MONTHLY REPORT ---------------- #

@attendance_bp.route("/monthly_report")
def monthly_report():

    today = datetime.utcnow()
    start_month = today.replace(day=1)

    records = Attendance.query.filter(
        Attendance.timestamp >= start_month
    ).all()

    return render_template(
        "monthly_report.html",
        records=records
    )