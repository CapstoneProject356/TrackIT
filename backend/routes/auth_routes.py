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


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    face_image = data.get("face_image")
    student_class = data.get("student_class")

    if not student_class:
        return jsonify(success=False, message="Class is required")

    valid_classes = ["FY", "SY", "TY"]
    if student_class not in valid_classes:
        return jsonify(success=False, message="Invalid class")

    user.student_class = student_class

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

    # STUDENT SPECIFIC VALIDATION
    if role == "student":
        roll = data.get("roll")
        dept = data.get("department")

        # Department required
        if not dept:
            return jsonify(success=False, message="Department is required")

        valid_departments = ["CO","IT", "ME", "CE", "EE","EJ"]  # Add more if needed
        if dept not in valid_departments:
            return jsonify(success=False, message="Invalid department selected")
        user.department = dept

        # Roll number required
        if not roll:
            return jsonify(success=False, message="Roll number is required")

        # INTEGER CHECK
        if not str(roll).isdigit():
            return jsonify(success=False, message="Roll number must be an integer")

        # Convert to integer
        roll = int(roll)
        user.roll_number = roll  # Make sure User model has `roll_number` column

        # Face capture required
        if not face_image:
            return jsonify(success=False, message="Face capture required")

        # SAVE FACE IMAGE
        image_data = face_image.split(",")[1]
        image_bytes = base64.b64decode(image_data)
        filename = f"{email}_{datetime.now().timestamp()}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(image_bytes)

        # SAVE PATH AND ENCODING
        user.face_image = filepath
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
    email = data.get('email')
    password = data.get('password')

    # FETCH USER BY EMAIL ONLY
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user)

        session["user_id"] = user.id
        session["role"] = user.role
        session["name"] = user.name

        return jsonify(success=True, role=user.role, user_id=user.id)

    return jsonify(success=False, message="Invalid credentials")


@auth_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect("/")  # Redirect to home page after logout