from flask import Blueprint, request, jsonify
import face_recognition

face_bp = Blueprint('face', __name__)

# In-memory face storage
registered_faces = {}  # user_id: encoding

@face_bp.route('/register', methods=['POST'])
def register_face():
    user_id = request.form['user_id']
    file = request.files['image']
    img = face_recognition.load_image_file(file)
    encoding = face_recognition.face_encodings(img)
    if encoding:
        registered_faces[user_id] = encoding[0]
        return jsonify({'status': 'success'})
    return jsonify({'status': 'fail', 'reason': 'Face not detected'})

@face_bp.route('/verify', methods=['POST'])
def verify_face():
    user_id = request.form['user_id']
    file = request.files['image']
    img = face_recognition.load_image_file(file)
    encoding = face_recognition.face_encodings(img)
    if encoding and user_id in registered_faces:
        match = face_recognition.compare_faces([registered_faces[user_id]], encoding[0])[0]
        return jsonify({'face_verified': match})
    return jsonify({'face_verified': False})
