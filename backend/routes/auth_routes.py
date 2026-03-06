from flask import Blueprint, request, jsonify
from backend.database.db_init import db
from ..models.user import User
import base64
import os
from datetime import datetime
auth_bp = Blueprint('auth', __name__)

UPLOAD_FOLDER = "backend/static/faces"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    face_image = data.get("face_image")

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already registered"})

    user = User(name=name, email=email, role=role)
    user.set_password(password)

    # Save face image for students
    if role == "student" and face_image:

        image_data = face_image.split(",")[1]
        image_bytes = base64.b64decode(image_data)

        filename = f"{email}_{datetime.now().timestamp()}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(image_bytes)

        user.face_image = filepath

    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        return jsonify(success=True, role=user.role, user_id=user.id)

    return jsonify(success=False, message="Invalid credentials")
