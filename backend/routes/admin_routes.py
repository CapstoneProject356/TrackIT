from flask import Blueprint, render_template, session, redirect, url_for, request
from backend.models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ================= MANAGE USERS PAGE =================
@admin_bp.route("/users")
def manage_users():

    if session.get("role") != "admin":
        return redirect(url_for("login_page"))

    return render_template("manage_users.html")

@admin_bp.route("/settings")
def system_settings():

    if session.get("role") != "admin":
        return redirect(url_for("login_page"))
    
    return render_template("system_settings.html")
# ================= STUDENTS =================
@admin_bp.route("/students")
def view_students():

    if session.get("role") != "admin":
        return redirect(url_for("login_page"))

    students = User.query.filter_by(role="student").all()

    return render_template("students_list.html", students=students)


# ================= FACULTY =================
@admin_bp.route("/faculty")
def view_faculty():

    if session.get("role") != "admin":
        return redirect(url_for("login_page"))

    faculty = User.query.filter_by(role="faculty").all()

    return render_template("faculty_list.html", faculty=faculty)

@admin_bp.route("/delete_user/<int:user_id>")
def delete_user(user_id):

    if session.get("role") != "admin":
        return redirect(url_for("login_page"))

    from backend.database.db_init import db
    from backend.models.user import User

    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect(request.referrer)