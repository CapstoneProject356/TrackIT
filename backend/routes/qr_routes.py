from flask import Blueprint, jsonify
import qrcode, io, base64
from datetime import datetime, timedelta
import uuid
from backend.utils.qr_generator import generate_qr
from backend.models.qr_session import QRSession
from backend.database.db_init import db

qr_bp = Blueprint('qr', __name__, url_prefix="/qr")

# ---------------- GENERATE QR ---------------- #
@qr_bp.route("/generate/<int:class_id>")
def generate_qr(class_id):
    # Generate a fully unique token
    teacher_id = 3
    session_id = uuid.uuid4().hex
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    token = f"class_id={class_id}|session={session_id}|ts={timestamp}"

    # Expiry 10 minutes
    expiry_time = datetime.utcnow() + timedelta(minutes=10)

    # Save session in DB
    qr_session = QRSession(
        teacher_id=3,  # replace with logged-in teacher
        token=token,
        expires_at=expiry_time,
        active=True
    )

    try:
        db.session.add(qr_session)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save QR session: {e}"}), 500

    # Generate QR image in base64
    qr_img = qrcode.make(token)
    img_io = io.BytesIO()
    qr_img.save(img_io, "PNG")
    img_io.seek(0)
    qr_base64 = base64.b64encode(img_io.getvalue()).decode()

    return jsonify({
        "session_id": qr_session.id,
        "token": token,
        "qr_image": f"data:image/png;base64,{qr_base64}",
        "expires_at": expiry_time.isoformat()
    })


# ---------------- VERIFY QR ---------------- #
from flask import request

@qr_bp.route("/verify", methods=["POST"])
def verify_qr():
    data = request.get_json()
    if not data or "token" not in data:
        return jsonify(valid=False)

    token = data["token"].strip()  # remove extra spaces
    print("TOKEN RECEIVED:", repr(token))
    # Find the session
    session = QRSession.query.filter_by(token=token, active=True).first()

    if not session:
        return jsonify(valid=False)

    # Check expiry
    if datetime.utcnow() > session.expires_at:
        session.active = False
        db.session.commit()
        return jsonify(valid=False)

    return jsonify(valid=True, session_id=session.id)