# backend/utils/qr_generator.py
import qrcode
import io
import base64
from datetime import datetime, timedelta
from backend.database.db_init import db
from backend.models.qr_session import QRSession

def generate_qr(class_id, teacher_id):
    # Create token exactly like you want: class_id=3|1773080973417
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    token = f"class_id={class_id}|{timestamp}"

    # Expiry in 2 minutes
    expiry = datetime.utcnow() + timedelta(minutes=2)

    # Save QR session to DB
    qr_session = QRSession(
        teacher_id=teacher_id,
        token=token,
        expires_at=expiry,
        active=True
    )

    db.session.add(qr_session)
    db.session.commit()

    # Generate QR image
    qr = qrcode.make(token)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "token": token,
        "qr_image": qr_base64,
        "expires_at": expiry.isoformat()
    }