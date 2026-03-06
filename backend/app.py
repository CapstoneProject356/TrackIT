from flask import Flask
from backend.database.db_init import db
from backend.routes.attendance_routes import attendance_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trackit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(attendance_bp)

if __name__ == "__main__":
    app.run(debug=True)