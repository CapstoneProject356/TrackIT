from flask import Blueprint, jsonify
import qrcode, io, base64
from datetime import datetime, timedelta

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/generate/<class_id>')
def generate_qr(class_id):
    expiry = (datetime.utcnow() + timedelta(seconds=60)).isoformat()
    data = f"{class_id}|{expiry}"

    qr_img = qrcode.make(data)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return jsonify({'qr_code': qr_base64, 'token': data})
