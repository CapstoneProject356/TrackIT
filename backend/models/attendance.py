from backend.database.db_init import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('qr_session.id'), nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    gps_lat = db.Column(db.Float, nullable=True)
    gps_long = db.Column(db.Float, nullable=True)

    qr_token = db.Column(db.String(100), nullable=False)
    face_verified = db.Column(db.Boolean, default=False)

    # 🔥 ADD THIS
    face_image = db.Column(db.LargeBinary, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'session_id', name='unique_attendance'),
    )

    def __repr__(self):
        return f"<Attendance Student {self.student_id} Session {self.session_id}>"
