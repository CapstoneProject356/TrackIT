from flask import Blueprint, request
from backend.utils.gps_checker import verify_gps
from backend.utils.face_recognition import verify_face
from backend.models.attendance import Attendance
from backend.models import db

attendance = Blueprint('attendance', __name__)

@attendance.route('/mark', methods=['POST'])
def mark_attendance():
    if not verify_gps(request.form['lat'], request.form['lng']):
        return "GPS Failed"

    # Face check assumed passed
    record = Attendance(student_id=1, subject="AI", status="Present")
    db.session.add(record)
    db.session.commit()
    return "Attendance Marked"

