def overall_statistics():
    from backend.models.attendance import Attendance
    from backend.models.user import User

    total_students = User.query.filter_by(role="student").count()
    total_attendance = Attendance.query.count()

    return {
        "total_students": total_students,
        "total_attendance_records": total_attendance
    }
