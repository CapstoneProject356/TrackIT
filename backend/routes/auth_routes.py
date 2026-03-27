from flask import Blueprint, request, jsonify, session, redirect
from backend.database.db_init import db
from ..models.user import User
from flask_login import login_user, logout_user
import base64
import os
from datetime import datetime
import face_recognition
import re

auth_bp = Blueprint('auth', __name__)

UPLOAD_FOLDER = "backend/static/faces"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ================= REGISTER =================
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    # REQUIRED FIELDS
    if not name or not email or not password or not role:
        return jsonify(success=False, message="All fields are required")

    # EMAIL FORMAT
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify(success=False, message="Invalid email format")

    # PASSWORD VALIDATION
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$', password):
        return jsonify(
            success=False,
            message="Password must be 8+ characters with letter, number and symbol"
        )

    # DUPLICATE EMAIL CHECK
    if User.query.filter_by(email=email).first():
        return jsonify(success=False, message="Email already registered")

    # CREATE USER
    user = User(name=name, email=email, role=role)
    user.set_password(password)

    # ================= STUDENT ONLY =================
    if role == "student":

        student_class = data.get("student_class")
        roll = data.get("roll")
        dept = data.get("department")
        face_image = data.get("face_image")

        # CLASS VALIDATION
        if not student_class:
            return jsonify(success=False, message="Class is required")

        if student_class not in ["FY", "SY", "TY"]:
            return jsonify(success=False, message="Invalid class")

        user.student_class = student_class

        # DEPARTMENT VALIDATION
        if not dept:
            return jsonify(success=False, message="Department is required")

        if dept not in ["CO", "IT", "ME", "CE", "EE", "EJ"]:
            return jsonify(success=False, message="Invalid department selected")

        user.department = dept

        # ROLL VALIDATION
        if not roll:
            return jsonify(success=False, message="Roll number is required")

        if not str(roll).isdigit():
            return jsonify(success=False, message="Roll number must be an integer")

        user.roll_number = int(roll)

        # FACE VALIDATION
        if not face_image:
            return jsonify(success=False, message="Face capture required")

        # SAVE FACE IMAGE
        image_data = face_image.split(",")[1]
        image_bytes = base64.b64decode(image_data)

        filename = f"{email}_{datetime.now().timestamp()}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(image_bytes)

        # SAVE PATH
        user.face_image = filepath

        # FACE ENCODING
        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            user.face_encoding = encodings[0].tolist()
        else:
            return jsonify(
                success=False,
                message="No face detected. Please register again."
            )

    # ================= SAVE USER =================
    db.session.add(user)
    db.session.commit()

    return jsonify(success=True)


# ================= LOGIN =================
@auth_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user)

        session["user_id"] = user.id
        session["role"] = user.role
        session["name"] = user.name

        return jsonify(success=True, role=user.role, user_id=user.id)

    return jsonify(success=False, message="Invalid credentials")


# ================= LOGOUT =================
@auth_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect("/")