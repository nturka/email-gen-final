from app import app, db

    # Ensure this script runs within the Flask application context
    with app.app_context():
        db.create_all() # This line MUST have exactly 4 spaces before it
        print("Database tables checked/created via init_db.py during build!") # This line MUST also have exactly 4 spaces before it
    