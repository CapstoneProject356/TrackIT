from backend.database.db_init import db
from datetime import datetime, timedelta

class QRSession(db.Model):
    __tablename__ = "qr_session"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, nullable=False)  
    token = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Session expiry (10 minutes)
    expires_at = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow() + timedelta(minutes=30)
    )

    active = db.Column(db.Boolean, default=True)
