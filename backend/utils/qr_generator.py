from backend.models.qr_session import QRSession
from backend.database.db_init import db
from datetime import datetime, timedelta
import uuid
from flask import current_app

def generate_qr(class_id, teacher_id, expiry_minutes=10):
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    session_id = uuid.uuid4().hex  # full UUID
    token = f"class_id={class_id}|session={session_id}|ts={timestamp}"
    expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)

    try:
        qr_session = QRSession(
            teacher_id=teacher_id,
            token=token,
            expires_at=expiry,
            active=True
        )
        db.session.add(qr_session)
        db.session.commit()
        print("✅ QR session saved:", qr_session.id, qr_session.token)
        return qr_session
    except Exception as e:
        db.session.rollback()
        print("❌ Failed to save QR session:", e)
        return None