from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# --- Flask App Configuration ---
app = Flask(__name__)

# Secret key for session management (IMPORTANT: Change this to a strong, random string in production!)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_key_here')
# Database configuration (SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Table Creation on App Startup ---
# This block ensures database tables are created when the app starts up,
# as Gunicorn imports and executes the global scope of app.py.
# This is crucial for ephemeral SQLite on Render's free tier, as the database file
# and its tables do not persist across restarts or deploys.
with app.app_context():
    db.create_all()
    print("Database tables checked/created on app startup!")

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# --- User Model for Database ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}')"

# --- Flask-Login User Loader ---
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- Routes ---

@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html', current_user=current_user)

# --- User Registration Route (REMOVED FOR MANUAL CREATION) ---
# The public /register route is removed to restrict who can create accounts.
# Users will now be created manually by the administrator.
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         if not username or not password:
#             flash('Username and password are required!', 'danger')
#             return render_template('register.html')
#         existing_user = User.query.filter_by(username=username).first()
#         if existing_user:
#             flash('Username already exists. Please choose a different one.', 'warning')
#             return render_template('register.html')
#         new_user = User(username=username)
#         new_user.set_password(password)
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Registration successful! You can now log in.', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html')

# --- User Login Route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('login.html')

    return render_template('login.html')

# --- User Logout Route ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- Manual User Creation Function (Run LOCALLY ONCE for each user) ---
# This function is NOT part of the web application routes.
# You run this directly from your terminal to add users to the database.
def create_initial_users():
    with app.app_context():
        # Create database tables if they don't exist (important for local first run)
        db.create_all()
        print("Database tables checked/created locally.")

        username = input("Enter username for new user: ")
        password = input(f"Enter password for {username}: ")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists. Skipping creation.")
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            print(f"User '{username}' created successfully!")

# --- Main Application Run (for local development or manual commands) ---
# This entire block is commented out when deploying to Render,
# as Gunicorn will be responsible for starting the app.
# When running locally to create users, you uncomment 'create_initial_users()'.
# When running locally for development, you uncomment 'app.run(debug=True)'.
#
# To use this block locally:
# 1. Uncomment the 'if __name__ == "__main__":' line.
# 2. Uncomment EITHER 'app.run(debug=True)' OR 'create_initial_users()', but NOT both at once.
# 3. Save app.py and run 'python app.py' in your terminal.
# 4. Re-comment the lines before pushing to Render.
#
# if __name__ == '__main__':
#     # app.run(debug=True)
#     # create_initial_users()
