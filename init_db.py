from app import app, db

# Ensure this script runs within the Flask application context
with app.app_context():
    db.create_all()
    print("Database tables checked/created via init_db.py during build!")