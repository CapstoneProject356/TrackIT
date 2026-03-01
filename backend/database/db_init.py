from backend.app import db, app

# Run within app context
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
