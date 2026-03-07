from flask import Blueprint, request, jsonify

from backend.models.attendance import Attendance
from backend.models.qr_session import QRSession
from backend.database.db_init import db
from backend.utils.gps_checker import verify_gps
from backend.utils.face_recognition import verify_face
from datetime import datetime

attendance_bp = Blueprint("attendance", __name__)


def verify_and_mark_attendance(student_id, session_id, face_image, latitude, longitude):

    session = QRSession.query.get(session_id)

    if not session or not session.is_active:
        return {"error": "Session expired"}

    if datetime.utcnow() > session.expires_at:
        session.is_active = False
        db.session.commit()
        return {"error": "QR expired"}

    # GPS Check
    if not verify_gps(latitude, longitude):
        return {"error": "Not inside classroom"}

    # Face Check
    if not verify_face(student_id, face_image):
        return {"error": "Face not matched"}

    attendance = Attendance(student_id=student_id, session_id=session_id)
    db.session.add(attendance)
    db.session.commit()

    return {"success": "Attendance marked"}
@attendance_bp.route("/mark_attendance", methods=["POST"])
def mark_attendance():

    student_id = request.form.get("student_id")
    session_id = request.form.get("session_id")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    face_image = request.files.get("face_image")

    if not student_id or not face_image:
        return jsonify({"error": "Missing data"})

    result = verify_and_mark_attendance(
        student_id,
        session_id,
        face_image,
        latitude,
        longitude
    )

    return jsonify(result)
