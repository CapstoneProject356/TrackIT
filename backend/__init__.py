from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register blueprints
    from backend.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Frontend routes
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
   
    @app.route('/daily_report')
    def daily_report_page():
        return render_template('daily_report.html')

    @app.route('/weekly_report')
    def weekly_report_page():
        return render_template('weekly_report.html')

    @app.route('/monthly_report')
    def monthly_report_page(): 
        return render_template('monthly_report.html')

    @app.route('/api/reports/daily')
    def daily_report():
    # Query DB and return JSON
        return jsonify([...])

    return app
