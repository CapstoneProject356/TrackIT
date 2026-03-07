import face_recognition
from backend.models.user import User

def verify_face(student_id, captured_file):

    user = User.query.get(student_id)

    if not user or not user.face_image:
        return False

    # Load stored image
    stored_image = face_recognition.load_image_file(user.face_image)
    stored_encoding = face_recognition.face_encodings(stored_image)

    if not stored_encoding:
        return False

    stored_encoding = stored_encoding[0]

    # Load captured image
    captured_image = face_recognition.load_image_file(captured_file)
    captured_encoding = face_recognition.face_encodings(captured_image)

    if not captured_encoding:
        return False

    captured_encoding = captured_encoding[0]

    result = face_recognition.compare_faces([stored_encoding], captured_encoding)

    return result[0]