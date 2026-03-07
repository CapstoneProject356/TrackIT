from flask import Blueprint, request, jsonify
from backend.database.db_init import db
from ..models.user import User
import base64
import os
from datetime import datetime
import face_recognition
import numpy as np
import re

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

    # REQUIRED FIELDS
    if not name or not email or not password:
        return jsonify(success=False, message="All fields are required")

    # EMAIL FORMAT
    email_regex = r"[^@]+@[^@]+\.[^@]+"

    if not re.match(email_regex, email):
        return jsonify(success=False, message="Invalid email format")

    # PASSWORD VALIDATION
    password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

    if not re.match(password_regex, password):
        return jsonify(
            success=False,
            message="Password must be 8+ characters with letter, number and symbol"
        )

    # DUPLICATE EMAIL
    if User.query.filter_by(email=email).first():
        return jsonify(success=False, message="Email already registered")

    user = User(name=name, email=email, role=role)
    user.set_password(password)

    # FACE SAVE + ENCODING
    if role == "student":

        if not face_image:
            return jsonify(success=False, message="Face capture required")

        image_data = face_image.split(",")[1]
        image_bytes = base64.b64decode(image_data)

        filename = f"{email}_{datetime.now().timestamp()}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(image_bytes)

        # save image path
        user.face_image = filepath

        # ⭐ FACE ENCODING GENERATION
        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            user.face_encoding = encodings[0].tolist()
        else:
            return jsonify(
                success=False,
                message="No face detected. Please register again."
            )

    db.session.add(user)
    db.session.commit()

    return jsonify(success=True)


@auth_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        return jsonify(success=True, role=user.role, user_id=user.id)

    return jsonify(success=False, message="Invalid credentials")