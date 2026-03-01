def calculate_percentage(student_id):
    from backend.models.attendance import Attendance
    from backend.models.qr_session import QRSession

    total_sessions = QRSession.query.count()
    attended = Attendance.query.filter_by(student_id=student_id).count()

    if total_sessions == 0:
        return 0

    return round((attended / total_sessions) * 100, 2)
