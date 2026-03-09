from flask import Blueprint, jsonify, request
import qrcode, io, base64
from datetime import datetime, timedelta
import uuid
from backend.models.qr_session import QRSession
from backend.database.db_init import db

qr_bp = Blueprint('qr', __name__, url_prefix="/qr")


# ---------------- GENERATE QR ---------------- #
# ---------------- GENERATE QR ---------------- #
@qr_bp.route("/generate/<int:class_id>")
def generate_qr(class_id):

    # QR valid for 10 minutes
    expiry_time = datetime.utcnow() + timedelta(minutes=10)

    # Unique session ID (short 6-char string)
    session_id = uuid.uuid4().hex[:6]

    # Create token in a simple key=value format
    token = f"class={class_id}|session={session_id}|expires={expiry_time.isoformat()}"

    # Save session in DB
    qr_session = QRSession(
        teacher_id=1,        # replace with logged-in teacher ID
        token=token,
        expires_at=expiry_time,
        active=True
    )

    db.session.add(qr_session)
    db.session.commit()

    # Generate QR image
    qr = qrcode.make(token)
    img_io = io.BytesIO()
    qr.save(img_io, "PNG")
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()

    # Return JSON (frontend can display image directly in base64)
    return jsonify({
        "session_id": qr_session.id,
        "token": token,
        "qr_image": f"data:image/png;base64,{img_base64}",  # ready for <img src=...>
        "expires_at": expiry_time.isoformat()
    })
    
# ---------------- VERIFY QR ---------------- #

# ---------------- VERIFY QR ---------------- #
@qr_bp.route('/verify', methods=['POST'])
def verify_qr():
    data = request.get_json()
    token = data.get("token")

    print("TOKEN RECEIVED:", token)  # Debug

    if not token:
        return jsonify(valid=False)

    token = token.strip()

    # Query session by exact token and active=True
    session = QRSession.query.filter_by(token=token, active=True).first()
    print("SESSION FOUND:", session)  # Debug

    if not session:
        return jsonify(valid=False)

    # Expiry check
    if datetime.utcnow() > session.expires_at:
        session.active = False
        db.session.commit()
        return jsonify(valid=False)

    # Everything okay, return valid=True and session_id
    return jsonify(valid=True, session_id=session.id)