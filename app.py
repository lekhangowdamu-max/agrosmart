from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

LOGO_URL = "/static/logo.svg"

# Database setup
DATABASE = 'agrosmart.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'farmer',
                phone TEXT,
                location TEXT,
                phone_verified INTEGER DEFAULT 0,
                photo TEXT,
                aadhaar TEXT,
                driving_license TEXT,
                ration_card TEXT,
                vehicle_number TEXT,
                vehicle_image TEXT
            )
        ''')
        conn.commit()

# User class
class User(UserMixin):
    def __init__(self, id, name, email, role, phone=None, location=None):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.phone = phone
        self.location = location

@login_manager.user_loader
def load_user(user_id):
    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            return User(user['id'], user['name'], user['email'], user['role'], user['phone'], user['location'])
    return None

@app.context_processor
def inject_user():
    return {
        "user": current_user if current_user.is_authenticated else None,
        "logo_url": LOGO_URL,
        "role": current_user.role if current_user.is_authenticated else None,
    }

init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            
        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['name'], user['email'], user['role'], user['phone'], user['location'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template("login.html", error="Invalid email or password")
    
    return render_template("login.html", error=None)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'farmer')
        phone = request.form.get('phone')
        location = request.form.get('location')
        
        # Basic validation
        if not all([name, email, password]):
            flash('All fields are required', 'error')
            return render_template("register.html", error="All fields are required")
        
        # Check if email already exists
        with get_db() as conn:
            existing = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
            if existing:
                flash('Email already registered', 'error')
                return render_template("register.html", error="Email already registered")
            
            # Hash password and insert
            hashed_password = generate_password_hash(password)
            conn.execute('''
                INSERT INTO users (name, email, password, role, phone, location)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, hashed_password, role, phone, location))
            conn.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html", error=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user_location=current_user.location or "Not set")

@app.route("/machinery")
def machinery():
    return render_template("machinery.html", machines=[])

@app.route("/prices", methods=["GET", "POST"])
def prices():
    return render_template("prices.html", prices=[], states=[], districts=[], crops=[], selected_state="", selected_district="", selected_crop="", gov_details=[], price_history=None, error=None, success=None)

@app.route("/map")
def map_view():
    return render_template("map.html", user_location="Not set", user_coords=None)

@app.route("/weather")
def weather():
    return render_template("weather.html", weather={"error": "Weather service temporarily disabled"})

@app.route("/motor")
def motor():
    return render_template("motor.html")

@app.route("/drone")
def drone():
    return render_template("drone.html")

@app.route("/cctv")
def cctv():
    return render_template("cctv.html")

# Temporarily disabled for Vercel debugging:
# - Database connections
# - External API calls
# - AI modules
# - Drone modules
# - Authentication logic
# - Heavy imports
# - Background services
# - Schema initialization

# Original AgroSmart code preserved below (commented out for minimal deployment)

"""
# Original app.py content disabled for minimal Vercel deployment
"""

if __name__ == "__main__":
    app.run(debug=True)