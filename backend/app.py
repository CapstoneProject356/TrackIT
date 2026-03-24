from backend import create_app
from backend.database.db_init import db

# IMPORT MODELS (IMPORTANT for SQLAlchemy foreign keys)
from backend.models.user import User
from backend.models.attendance import Attendance
from backend.models.qr_session import QRSession
# IMPORT ROUTES
from backend.routes.face_routes import face_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.attendance_routes import attendance_bp
from backend.routes.gps_routes import gps_bp
from backend.routes.qr_routes import qr_bp
from backend.routes.admin_routes import admin_bp

app = create_app()

# Register blueprints
app.register_blueprint(face_bp)
app.register_blueprint(gps_bp)
app.register_blueprint(qr_bp, url_prefix="/qr")
app.register_blueprint(attendance_bp, url_prefix="/attendance")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(admin_bp)

if __name__ == "__main__":

    # Create tables
    with app.app_context():
         from backend.utils.qr_generator import generate_qr
         generate_qr(class_id=1, teacher_id=1)
         db.create_all()

    app.run(debug=True, use_reloader=False)