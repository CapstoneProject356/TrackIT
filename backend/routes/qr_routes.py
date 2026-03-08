from flask import Blueprint, jsonify,request
import qrcode, io, base64
from datetime import datetime, timedelta

qr_bp = Blueprint('qr', __name__)

# Validate QR token
def is_qr_valid(token_data):
    try:
        token_data = token_data.strip()
        class_part, expiry_str = token_data.split("|")
        class_id = class_part.split("=")[1]
        expiry_time = datetime.fromisoformat(expiry_str)  # ISO format required
        return datetime.utcnow() <= expiry_time
    except Exception as e:
        print("QR validation error:", e)
        return False

# Generate QR for a class
@qr_bp.route('/generate/<class_id>')
def generate_qr(class_id):
    # Set expiry 30 minutes from now
    expiry_time = datetime.utcnow() + timedelta(minutes=30)
    expiry_str = expiry_time.isoformat()  # Convert to ISO string

    # QR format: class_id=1|2026-03-08T19:30:00
    qr_data = f"class_id={class_id}|{expiry_str}"

    qr_img = qrcode.make(qr_data)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    qr_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return jsonify({
        "qr_code": qr_base64,
        "token": qr_data
    })

# Verify QR
@qr_bp.route('/verify', methods=['POST'])
def verify_qr():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify(valid=False)

    # If token contains full URL, extract it
    if "token=" in token:
        token = token.split("token=")[-1]

    token = token.strip()

    if is_qr_valid(token):
        return jsonify(valid=True, token=token)
    return jsonify(valid=False)