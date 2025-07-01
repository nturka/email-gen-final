from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# --- Flask App Configuration ---
app = Flask(__name__)

# Secret key for session management (IMPORTANT: Change this to a strong, random string in production!)
# It's good practice to use an environment variable for the secret key in production.
# For local testing, 'your_super_secret_key_here' will work.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_key_here')
# Database configuration (SQLite for simplicity)
# This creates a file named site.db in your root folder.
# On Render's free tier, this database file will be created on each deploy and will not persist data
# across deploys or restarts. For persistent data, you'd need a separate database service (e.g., Render PostgreSQL).
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Suppress a warning

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # The route name for the login page (where to redirect if not logged in)
login_manager.login_message_category = 'info' # Category for flash messages (e.g., 'Please log in to access this page.')

# --- User Model for Database ---
# This defines the structure of your 'users' table in the database.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) # Stores the hashed password

    def set_password(self, password):
        """Hashes the given password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the given password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """String representation for debugging."""
        return f"User('{self.username}')"

# --- Flask-Login User Loader ---
# This function is crucial for Flask-Login. It tells Flask-Login how to load a user
# from their ID, which is stored in the session.
@login_manager.user_loader
def load_user(user_id):
    """Callback to reload the user object from the user ID stored in the session."""
    return db.session.get(User, int(user_id)) # Using db.session.get for Flask-SQLAlchemy 3.x

# --- Routes ---

# Main Email Generator Page (Protected)
# Only authenticated users can access this page.
@app.route('/', methods=['GET'])
@login_required # This decorator protects the route, redirects to login if not authenticated
def index():
    # The email generation logic is handled by JavaScript on the client-side (in index.html).
    # We pass current_user to the template so it can display login/logout links.
    return render_template('index.html', current_user=current_user)

# User Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    # If the user is already logged in, redirect them to the main page.
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Basic server-side validation
        if not username or not password:
            flash('Username and password are required!', 'danger')
            return render_template('register.html')

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'warning')
            return render_template('register.html')

        # Create new user and hash password
        new_user = User(username=username)
        new_user.set_password(password) # Hash the password before saving
        db.session.add(new_user)
        db.session.commit() # Save the new user to the database

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login')) # Redirect to login page after successful registration

    # For GET request, just render the registration form
    return render_template('register.html')

# User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is already logged in, redirect them to the main page.
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Find user by username
        user = User.query.filter_by(username=username).first()
        # Check if user exists and password is correct
        if user and user.check_password(password):
            login_user(user) # Log the user in using Flask-Login
            flash('Logged in successfully!', 'success')
            # Redirect to the 'next' page if they were trying to access a protected route
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('login.html')

    # For GET request, just render the login form
    return render_template('login.html')

# User Logout Route
@app.route('/logout')
@login_required # Only logged-in users can logout
def logout():
    logout_user() # Log the user out using Flask-Login
    flash('You have been logged out.', 'info')
    return redirect(url_for('login')) # Redirect to login page after logout

# --- Database Initialization (Run this ONCE locally to create site.db) ---
# This function creates the database tables based on your User model.
# You should run this locally ONCE before your first deployment or first local run
# to create the 'site.db' file.
# On Render, the database file will be created automatically if it doesn't exist
# when the app starts and tries to access it, but it won't persist across deploys
# on the free tier. For persistent data, you'd need a separate database service.
def create_db():
    with app.app_context(): # Ensures Flask application context is active
        db.create_all() # Creates all tables defined by db.Model classes
        print("Database tables created!")

# --- Main Application Run (for local development only) ---
# This block is commented out because Gunicorn will be responsible for starting the app on Render.
# When deploying with Gunicorn, Gunicorn directly imports and runs the 'app' instance.
# if __name__ == '__main__': # <--- RE-COMMENTED
#     # Call create_db() once to set up your local database
#     # create_db()
#     app.run(debug=True)

