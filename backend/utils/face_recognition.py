import face_recognition

def verify_face(known_encoding, image):
    unknown = face_recognition.face_encodings(image)
    if not unknown:
        return False
    return face_recognition.compare_faces([known_encoding], unknown[0])[0]
