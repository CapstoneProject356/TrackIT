from flask import Blueprint, render_template
from backend.models.attendance import Attendance
from datetime import date, timedelta

student = Blueprint('student', __name__)

@student.route('/student/reports')
def reports():
    today = date.today()
    week = today - timedelta(days=7)

    daily = Attendance.query.filter_by(date=today).all()
    weekly = Attendance.query.filter(Attendance.date >= week).all()

    return render_template('reports.html', daily=daily, weekly=weekly)
