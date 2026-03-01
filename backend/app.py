from backend import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
from backend.routes.attendance_routes import attendance_bp
app.register_blueprint(attendance_bp)

# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('base.html')

# if __name__ == "__main__":
#     app.run(debug=True)

