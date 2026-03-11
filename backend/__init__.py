from flask import Flask, render_template, jsonify
from backend.database.db_init import db
from .config import Config
from flask import session, request, redirect, url_for 
from backend.models.user import User
from flask_login import LoginManager


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trackit.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize DB
    db.init_app(app)
    
    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login_page"  # route name for login

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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
    
    @app.route('/dashboard')
    def dashboard_page():
        role = session.get("role")

        if role == "student":
            return render_template("student_dashboard.html")

        elif role == "faculty":
            return render_template("faculty_dashboard.html")

        elif role == "admin":
           return render_template("admin_dashboard.html")

        else:
           return redirect(url_for("login_page"))
    
    @app.route("/logout") 
    def logout():
        session.clear()
        return redirect(url_for("auth.login"))

    

    # ================= SAMPLE REPORT API =================

    @app.route('/api/reports/daily')
    def daily_report():

        data = [
            {"name": "Student 1", "status": "Present"},
            {"name": "Student 2", "status": "Absent"}
        ]

        return jsonify(data)
    
    # ----------------- Faculty Profile Routes -----------------
    @app.route("/faculty/profile")
    def faculty_profile_page():
        return render_template("faculty_profile.html")

    @app.route("/faculty/profile/get")
    def get_faculty_profile():
       user_id = session.get("user_id")
       if not user_id:
           return jsonify({"error": "Not logged in"}), 401

       user = User.query.get(user_id)
       if not user:
           return jsonify({"error": "User not found"}), 404

       return jsonify({
       "id": user.id,
        "name": user.name,
        "email": user.email,
        #"subject": getattr(user, "subject", "")
    })

    @app.route("/faculty/profile/update", methods=["POST"])
    def update_faculty_profile():
       user_id = session.get("user_id")
       if not user_id:
           return jsonify({"error": "Not logged in"}), 401

       user = User.query.get(user_id)
       if not user:
           return jsonify({"error": "User not found"}), 404

    # Update fields
       user.name = request.form.get("name", user.name)
       user.email = request.form.get("email", user.email)
      # user.subject = request.form.get("subject", getattr(user, "subject", ""))

       try:
           db.session.commit()
           return jsonify({"success": True})
       except Exception as e:
          db.session.rollback()
          return jsonify({"success": False, "error": str(e)})


# ----------------- Student Profile Routes -----------------
    @app.route("/student/profile")
    def student_profile_page():
       return render_template("student_profile.html")

    @app.route("/student/profile/get")
    def get_student_profile():
       user_id = session.get("user_id")
       if not user_id:
           return jsonify({"error": "Not logged in"}), 401

       user = User.query.get(user_id)
       if not user:
           return jsonify({"error": "User not found"}), 404

       return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        # "subject": getattr(user, "subject", "")
    })

    @app.route("/student/profile/update", methods=["POST"])
    def update_student_profile():
       user_id = session.get("user_id")
       if not user_id:
           return jsonify({"error": "Not logged in"}), 401

       user = User.query.get(user_id)
       if not user:
           return jsonify({"error": "User not found"}), 404

       user.name = request.form.get("name", user.name)
       user.email = request.form.get("email", user.email)
    # user.subject = request.form.get("subject", getattr(user, "subject", ""))

       try:
           db.session.commit()
           return jsonify({"success": True})
       except Exception as e:
          db.session.rollback()
          return jsonify({"success": False, "error": str(e)})


    return app