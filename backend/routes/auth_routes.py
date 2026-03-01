from flask import Blueprint, request, jsonify
from .. import db
from ..models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify(success=False, message="No data received")

    if User.query.filter_by(email=data['email']).first():
        return jsonify(success=False, message="User already exists")

    user = User(
        name=data['name'],
        email=data['email'],
        role=data['role']
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify(success=True, message="Registration successful")


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        return jsonify(success=True, role=user.role, user_id=user.id)

    return jsonify(success=False, message="Invalid credentials")
