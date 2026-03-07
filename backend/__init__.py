from flask import Flask, render_template, jsonify
from backend.database.db_init import db
from .config import Config

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trackit.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize DB
    db.init_app(app)

    # ================= FRONTEND ROUTES =================

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/student_dashboard')
    def student_dashboard():
        return render_template('student_dashboard.html')

    @app.route('/faculty_dashboard')
    def faculty_dashboard():
        return render_template('faculty_dashboard.html')

    @app.route('/admin_dashboard')
    def admin_dashboard():
        return render_template('admin_dashboard.html')

    @app.route('/attendance')
    def attendance_page():
        return render_template('attendance.html')

    @app.route('/about')
    def about_page():
        return render_template('about.html')

    @app.route('/reports')
    def reports_page():
        return render_template('reports.html')

    # ================= SAMPLE REPORT API =================

    @app.route('/api/reports/daily')
    def daily_report():

        data = [
            {"name": "Student 1", "status": "Present"},
            {"name": "Student 2", "status": "Absent"}
        ]

        return jsonify(data)

    return app