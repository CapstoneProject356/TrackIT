from flask import Blueprint, request, jsonify
import face_recognition
import numpy as np
from backend.models.user import User
import tempfile
from backend.database.db_init import db

face_bp = Blueprint('face', __name__)

@face_bp.route("/face/verify", methods=["POST"])
def verify_face():

    print("Face verify request received")

    if "image" not in request.files:
        print("No image received")
        return jsonify(face_verified=False)

    user_id = request.form.get("user_id")

    if not user_id:
        print("No user_id received")
        return jsonify(face_verified=False)

    user = db.session.get(User, int(user_id))

    if not user:
        print("User not found")
        return jsonify(face_verified=False)

    if not user.face_encoding:
        print("User has no stored face encoding")
        return jsonify(face_verified=False)

    image_file = request.files["image"]

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        image_file.save(temp.name)
        temp_path = temp.name

    unknown_image = face_recognition.load_image_file(temp_path)
    face_locations = face_recognition.face_locations(unknown_image)
    print("Faces found:", len(face_locations))
    unknown_encodings = face_recognition.face_encodings(unknown_image, face_locations)

    if not unknown_encodings:
        print("No face detected in image")
        return jsonify(face_verified=False)

    unknown_encoding = unknown_encodings[0]

    known_encoding = np.array(user.face_encoding)

    distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]

    match = distance < 0.6

    print("User ID:", user_id)
    print("Detected faces:", len(unknown_encodings))
    print("Face distance:", distance)
    print("Match result:", match)

    return jsonify(face_verified=bool(match))