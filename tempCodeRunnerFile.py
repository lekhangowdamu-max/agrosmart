from flask import Flask, render_template, request, redirect, session, jsonify, flash
from werkzeug.utils import secure_filename
import mysql.connector
import requests
from bs4 import BeautifulSoup
import os
import random
import threading
import math
from datetime import datetime
from urllib.parse import quote_plus
app = Flask(__name__)
app.secret_key = "agrosmart_secret"
LOGO_URL = "/static/logo.svg"
GOOGLE_MAPS_API_KEY = "AIzaSyD-2rQJtoNtSKxnI9ExHnGAd_CuKK7yj1Q"
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_PHOTO_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.context_processor
def inject_user():
    return {
        "user": session.get("user"),
        "logo_url": LOGO_URL,
        "role": session.get("role"),
    }

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("user_email", None)
    session.pop("user_location", None)
    session.pop("role", None)
    session.pop("pending_registration", None)
    session.pop("otp_sent_to", None)
    return redirect("/")

# DB Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="LEKHAN@2121",
    database="agrosmart"
)
cursor = db.cursor(dictionary=True)


def ensure_user_schema():
    try:
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            cursor.execute(
                """CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100) UNIQUE,
                    password VARCHAR(100),
                    location VARCHAR(150),
                    phone VARCHAR(20),
                    role ENUM('farmer','admin') DEFAULT 'farmer',
                    phone_verified TINYINT(1) DEFAULT 0,
                    photo VARCHAR(255),
                    aadhaar VARCHAR(50),
                    driving_license VARCHAR(100),
                    ration_card VARCHAR(100),
                    vehicle_number VARCHAR(100),
                    vehicle_image VARCHAR(255)
                )"""
            )
            db.commit()
        else:
            fields = [
                ("location", "VARCHAR(150)"),
                ("phone", "VARCHAR(20)"),
                ("role", "ENUM('farmer','admin') DEFAULT 'farmer'"),
                ("phone_verified", "TINYINT(1) DEFAULT 0"),
                ("photo", "VARCHAR(255)"),
                ("aadhaar", "VARCHAR(50)"),
                ("driving_license", "VARCHAR(100)"),
                ("ration_card", "VARCHAR(100)"),
                ("vehicle_number", "VARCHAR(100)"),
                ("vehicle_image", "VARCHAR(255)")
            ]
            for field_name, field_type in fields:
                cursor.execute(f"SHOW COLUMNS FROM users LIKE '{field_name}'")
                if not cursor.fetchone():
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}")
                    db.commit()
    except mysql.connector.Error as err:
        print("Schema check error:", err)

ensure_user_schema()

def ensure_booking_schema():
    try:
        # Check if bookings table exists
        cursor.execute("SHOW TABLES LIKE 'bookings'")
        if not cursor.fetchone():
            # Create the bookings table with new schema
            cursor.execute("""
                CREATE TABLE bookings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    machine_id INT,
                    user_id INT,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    status ENUM('pending', 'approved', 'rejected', 'cancelled', 'completed') DEFAULT 'pending',
                    total_cost DECIMAL(10,2),
                    notes TEXT,
                    farmer_location VARCHAR(150),
                    accepted_by_admin_id INT,
                    admin_phone VARCHAR(20),
                    admin_photo VARCHAR(255),
                    admin_vehicle_number VARCHAR(100),
                    admin_location VARCHAR(150),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (machine_id) REFERENCES machinery(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            db.commit()
            print("Created bookings table with new schema")
        else:
            required_columns = [
                "farmer_location",
                "accepted_by_admin_id",
                "admin_phone",
                "admin_photo",
                "admin_vehicle_number",
                "admin_location"
            ]
            for column in required_columns:
                cursor.execute(f"SHOW COLUMNS FROM bookings LIKE '{column}'")
                if not cursor.fetchone():
                    if column == "accepted_by_admin_id":
                        cursor.execute(f"ALTER TABLE bookings ADD COLUMN {column} INT NULL")
                    elif column == "farmer_location":
                        cursor.execute(f"ALTER TABLE bookings ADD COLUMN {column} VARCHAR(150)")
                    else:
                        cursor.execute(f"ALTER TABLE bookings ADD COLUMN {column} VARCHAR(255)")
                    db.commit()
            print("Bookings schema is up to date")
    except Exception as err:
        print("Booking schema check error:", str(err))
        import traceback
        traceback.print_exc()

ensure_booking_schema()

def ensure_machinery_schema():
    try:
        cursor.execute("SHOW TABLES LIKE 'machinery'")
        if cursor.fetchone():
            cursor.execute("SHOW COLUMNS FROM machinery LIKE 'image_url'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE machinery ADD COLUMN image_url VARCHAR(255) NULL")
                db.commit()
            cursor.execute("SHOW COLUMNS FROM machinery LIKE 'tracking_location'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE machinery ADD COLUMN tracking_location VARCHAR(255) NULL")
                db.commit()
    except mysql.connector.Error as err:
        print("Machinery schema check error:", err)

ensure_machinery_schema()

def ensure_crop_prices_schema():
    try:
        cursor.execute("SHOW TABLES LIKE 'crop_prices'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE crop_prices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    crop_name VARCHAR(100),
                    market_name VARCHAR(100),
                    price DECIMAL(10,2),
                    location VARCHAR(150),
                    date DATE
                )
            """)
            db.commit()
            print("Created crop_prices table")
    except mysql.connector.Error as err:
        print("Crop prices schema check error:", err)

ensure_crop_prices_schema()

# ---------------- DRONE STATE ----------------
DRONE_STATE = {
    "id": "agro-drone-001",
    "name": "AgroScout",
    "status": "grounded",
    "battery": 100,
    "altitude": 0,
    "speed": 0,
    "latitude": 26.912400,
    "longitude": 75.787300,
    "heading": 0,
    "signal": 100,
    "mode": "idle",
    "last_command": "none",
    "waypoint": None,
    "logs": [
        {"time": datetime.utcnow().isoformat(), "event": "Drone control initialized", "level": "info"}
    ],
    "last_update": datetime.utcnow()
}
DRONE_LOCK = threading.Lock()


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def add_drone_log(event, level="info"):
    DRONE_STATE["logs"].insert(0, {"time": datetime.utcnow().isoformat(), "event": event, "level": level})
    if len(DRONE_STATE["logs"]) > 20:
        DRONE_STATE["logs"].pop()


def update_drone_state():
    with DRONE_LOCK:
        now = datetime.utcnow()
        elapsed = (now - DRONE_STATE["last_update"]).total_seconds()
        if elapsed <= 0:
            return
        DRONE_STATE["last_update"] = now

        if DRONE_STATE["status"] == "airborne":
            DRONE_STATE["battery"] = clamp(DRONE_STATE["battery"] - 0.25 * elapsed, 0, 100)
            DRONE_STATE["signal"] = clamp(DRONE_STATE["signal"] + random.uniform(-1.5, 0.8) * elapsed, 20, 100)
        else:
            DRONE_STATE["signal"] = clamp(DRONE_STATE["signal"] + random.uniform(-0.6, 0.8) * elapsed, 35, 100)

        if DRONE_STATE["status"] == "landing":
            DRONE_STATE["altitude"] = clamp(DRONE_STATE["altitude"] - 20 * elapsed, 0, DRONE_STATE["altitude"])
            DRONE_STATE["speed"] = clamp(DRONE_STATE["speed"] - 8 * elapsed, 0, 30)
            if DRONE_STATE["altitude"] <= 0:
                DRONE_STATE["status"] = "grounded"
                DRONE_STATE["mode"] = "idle"
                DRONE_STATE["speed"] = 0
                add_drone_log("Landing complete", "success")

        if DRONE_STATE["status"] == "emergency":
            DRONE_STATE["altitude"] = clamp(DRONE_STATE["altitude"] - 30 * elapsed, 0, DRONE_STATE["altitude"])
            DRONE_STATE["speed"] = 0
            if DRONE_STATE["altitude"] <= 0:
                DRONE_STATE["status"] = "grounded"
                DRONE_STATE["mode"] = "idle"
                add_drone_log("Emergency stop complete", "error")

        if DRONE_STATE["status"] == "airborne":
            if DRONE_STATE["waypoint"]:
                target = DRONE_STATE["waypoint"]
                dx = target["latitude"] - DRONE_STATE["latitude"]
                dy = target["longitude"] - DRONE_STATE["longitude"]
                distance = math.sqrt(dx * dx + dy * dy)
                travel = 0.00003 * (DRONE_STATE["speed"] + 20) * elapsed
                if distance < travel or distance == 0:
                    DRONE_STATE["latitude"] = target["latitude"]
                    DRONE_STATE["longitude"] = target["longitude"]
                    DRONE_STATE["waypoint"] = None
                    DRONE_STATE["mode"] = "hover"
                    add_drone_log("Waypoint reached", "success")
                else:
                    ratio = travel / distance
                    DRONE_STATE["latitude"] += dx * ratio
                    DRONE_STATE["longitude"] += dy * ratio
                    DRONE_STATE["heading"] = round((math.degrees(math.atan2(dy, dx)) + 360) % 360)
                    DRONE_STATE["mode"] = "navigation"
            else:
                heading_rad = math.radians(DRONE_STATE["heading"])
                drift = 0.00002 * DRONE_STATE["speed"] * elapsed
                DRONE_STATE["latitude"] = round(DRONE_STATE["latitude"] + math.cos(heading_rad) * drift, 6)
                DRONE_STATE["longitude"] = round(DRONE_STATE["longitude"] + math.sin(heading_rad) * drift, 6)

        if DRONE_STATE["battery"] <= 15 and DRONE_STATE["status"] == "airborne" and DRONE_STATE["mode"] != "returning":
            DRONE_STATE["mode"] = "returning"
            add_drone_log("Low battery: return to home recommended", "warning")


def execute_drone_command(action, payload=None):
    with DRONE_LOCK:
        if payload is None:
            payload = {}
        DRONE_STATE["last_command"] = action

        if action == "takeoff" and DRONE_STATE["status"] in ["grounded", "idle"]:
            DRONE_STATE["status"] = "airborne"
            DRONE_STATE["altitude"] = 70
            DRONE_STATE["speed"] = 24
            DRONE_STATE["mode"] = "takeoff"
            add_drone_log("Takeoff initiated", "info")
        elif action == "land" and DRONE_STATE["status"] == "airborne":
            DRONE_STATE["status"] = "landing"
            DRONE_STATE["speed"] = 18
            DRONE_STATE["mode"] = "landing"
            add_drone_log("Landing sequence started", "info")
        elif action == "emergency":
            DRONE_STATE["status"] = "emergency"
            DRONE_STATE["speed"] = 0
            DRONE_STATE["mode"] = "emergency stop"
            add_drone_log("Emergency stop activated", "error")
        elif action == "move" and DRONE_STATE["status"] == "airborne":
            direction = payload.get("direction", "forward")
            mapping = {"forward": 0, "backward": 180, "left": 270, "right": 90}
            DRONE_STATE["heading"] = mapping.get(direction, DRONE_STATE["heading"])
            DRONE_STATE["speed"] = clamp(DRONE_STATE["speed"] + 8, 10, 80)
            DRONE_STATE["mode"] = "manual flight"
            add_drone_log(f"Moving {direction}", "info")
        elif action == "setAltitude" and DRONE_STATE["status"] == "airborne":
            DRONE_STATE["altitude"] = clamp(payload.get("altitude", DRONE_STATE["altitude"]), 0, 500)
            add_drone_log(f"Altitude adjusted to {DRONE_STATE['altitude']}m", "info")
        elif action == "setSpeed" and DRONE_STATE["status"] == "airborne":
            DRONE_STATE["speed"] = clamp(payload.get("speed", DRONE_STATE["speed"]), 0, 100)
            add_drone_log(f"Speed adjusted to {DRONE_STATE['speed']}%", "info")
        elif action == "spray" and DRONE_STATE["status"] == "airborne":
            DRONE_STATE["mode"] = "spray" if DRONE_STATE["mode"] != "spray" else "hover"
            add_drone_log("Spray mode toggled", "info")
        elif action == "monitor" and DRONE_STATE["status"] == "airborne":
            DRONE_STATE["mode"] = "crop monitoring"
            add_drone_log("Crop monitoring activated", "info")
        elif action == "setWaypoint" and DRONE_STATE["status"] == "airborne":
            waypoint = {
                "latitude": payload.get("latitude", DRONE_STATE["latitude"]),
                "longitude": payload.get("longitude", DRONE_STATE["longitude"])
            }
            DRONE_STATE["waypoint"] = waypoint
            DRONE_STATE["mode"] = "navigation"
            add_drone_log(f"Waypoint set: {waypoint['latitude']:.5f}, {waypoint['longitude']:.5f}", "info")
        else:
            add_drone_log(f"Ignored command: {action}", "warning")


def get_drone_state_for_client():
    with DRONE_LOCK:
        update_drone_state()
        state = {k: v for k, v in DRONE_STATE.items() if k != "last_update"}
        if state["waypoint"] is None:
            state["waypoint"] = None
        return state


# ---------------- HELPERS ----------------
def allowed_photo_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_PHOTO_EXTENSIONS


def save_uploaded_image(photo_file, owner_label, suffix):
    if not photo_file or photo_file.filename == "":
        return None
    if not allowed_photo_file(photo_file.filename):
        return None

    extension = secure_filename(photo_file.filename).rsplit(".", 1)[1].lower()
    safe_owner = secure_filename(owner_label.replace("@", "_"))
    filename = f"{safe_owner}_{suffix}_{random.randint(1000,9999)}.{extension}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    photo_file.save(save_path)
    return f"uploads/{filename}"


def save_profile_photo(photo_file, email):
    return save_uploaded_image(photo_file, email, "profile")


def save_vehicle_photo(photo_file, email):
    return save_uploaded_image(photo_file, email, "vehicle")


def generate_otp():
    return str(random.randint(100000, 999999))


def fetch_gov_crop_details():
    url = "https://agmarknet.gov.in/MarketReport.aspx"
    crops = []
    try:
        response = requests.get
        response.raise_for_status()(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
        select = soup.select_one("select[name*='Commodity'], select[id*='Commodity']")
        if select:
            crops = [option.text.strip() for option in select.find_all("option") if option.text.strip()]
    except Exception:
        crops = []

    if crops:
        return [{"crop": crop, "source": "agmarknet.gov.in"} for crop in crops[:12]]

    return [
        {"crop": "Wheat", "source": "gov.in sample"},
        {"crop": "Rice", "source": "gov.in sample"},
        {"crop": "Maize", "source": "gov.in sample"},
        {"crop": "Sugarcane", "source": "gov.in sample"},
        {"crop": "Cotton", "source": "gov.in sample"},
    ]


def fetch_openweather(location):
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        return {"error": "Live weather requires OPENWEATHER_API_KEY in environment."}

    query = location if location and location != "Not set" else "New Delhi,IN"
    url = "https://api.openweathermap.org/data/2.5/weather"
    try:
        response = requests.get
        response.raise_for_status()(
            url,
            params={"q": query, "appid": api_key, "units": "metric"},
            timeout=30,
        )
        data = response.json()
        if response.status_code != 200:
            return {"error": data.get("message", "Unable to fetch weather data.")}

        return {
            "location": f"{data.get('name', query)}, {data.get('sys', {}).get('country', '')}".strip(", "),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "description": data["weather"][0]["description"].title(),
            "humidity": data["main"]["humidity"],
            "wind": data["wind"]["speed"],
        }
    except Exception as err:
        return {"error": f"Unable to fetch weather: {err}"}


def geocode_location(location):
    if not location or location == "Not set":
        return None

    try:
        url = "https://nominatim.openstreetmap.org/search"
        response = requests.get
        response.raise_for_status()(
            url,
            params={"q": location, "format": "json", "limit": 1},
            headers={"User-Agent": "AgroSmart/1.0"},
            timeout=30,
        )
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


def search_locations(query, limit=6):
    if not query:
        return []

    try:
        url = "https://nominatim.openstreetmap.org/search"
        response = requests.get
        response.raise_for_status()(
            url,
            params={"q": query, "format": "json", "limit": limit, "addressdetails": 1},
            headers={"User-Agent": "AgroSmart/1.0"},
            timeout=30,
        )
        data = response.json()
        return [
            {
                "display_name": item.get("display_name"),
                "lat": float(item["lat"]),
                "lon": float(item["lon"]),
                "type": item.get("type", ""),
            }
            for item in data
        ]
    except Exception:
        return []


@app.route("/search_location")
def search_location():
    query = request.args.get("q", "").strip()
    results = search_locations(query)
    return jsonify(results)


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- AUTH ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        if session.get("role") == "admin":
            return redirect("/admin")
        return redirect("/dashboard")

    error = None
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()

        if user:
            session["user"] = user["name"]
            session["user_id"] = user["id"]
            session["user_email"] = user["email"]
            session["user_location"] = user.get("location", "Not set")
            session["role"] = user.get("role", "farmer")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            if session["role"] == "admin":
                return redirect("/admin")
            return redirect("/dashboard")

        error = "Invalid email or password. Please try again."

    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user"):
        if session.get("role") == "admin":
            return redirect("/admin")
        return redirect("/dashboard")

    error = None
    if request.method == "POST":
        role = request.form.get("role", "farmer")
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        location = request.form.get("location", "Not set").strip()
        phone = request.form.get("phone", "").strip()
        photo_file = request.files.get("photo")
        aadhaar = request.form.get("aadhaar", "").strip()
        driving_license = request.form.get("driving_license", "").strip()
        ration_card = request.form.get("ration_card", "").strip()
        vehicle_number = request.form.get("vehicle_number", "").strip()
        vehicle_image_file = request.files.get("vehicle_image")

        if not name or not email or not password or not phone or not location:
            error = "Please fill in all required fields."
        elif photo_file and photo_file.filename and not allowed_photo_file(photo_file.filename):
            error = "Invalid profile photo file type. Please upload PNG, JPG, JPEG, GIF, or WebP."
        elif role == "admin" and (not aadhaar or not driving_license or not ration_card or not vehicle_number):
            error = "Admin registration requires Aadhaar, driving license, ration card, and registered vehicle number."
        elif role == "admin" and (not vehicle_image_file or not vehicle_image_file.filename):
            error = "Admin registration requires an uploaded vehicle image."
        elif role == "admin" and vehicle_image_file and not allowed_photo_file(vehicle_image_file.filename):
            error = "Invalid vehicle image file type. Please upload PNG, JPG, JPEG, GIF, or WebP."
        else:
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                error = "A user with that email already exists."
            else:
                photo_path = save_profile_photo(photo_file, email)
                vehicle_image_path = save_vehicle_photo(vehicle_image_file, email) if role == "admin" else None
                otp_code = generate_otp()
                session["pending_registration"] = {
                    "role": role,
                    "name": name,
                    "email": email,
                    "password": password,
                    "location": location,
                    "phone": phone,
                    "photo": photo_path,
                    "aadhaar": aadhaar,
                    "driving_license": driving_license,
                    "ration_card": ration_card,
                    "vehicle_number": vehicle_number,
                    "vehicle_image": vehicle_image_path,
                    "otp": otp_code,
                }
                session["otp_sent_to"] = phone
                return redirect("/verify-otp")

    return render_template("register.html", error=error)

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    pending = session.get("pending_registration")
    if not pending:
        return redirect("/register")

    error = None
    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        if entered_otp == pending.get("otp"):
            try:
                cursor.execute(
                    "INSERT INTO users(name,email,password,location,phone,role,phone_verified,photo,aadhaar,driving_license,ration_card,vehicle_number,vehicle_image) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        pending["name"],
                        pending["email"],
                        pending["password"],
                        pending["location"],
                        pending["phone"],
                        pending.get("role", "farmer"),
                        1,
                        pending.get("photo"),
                        pending.get("aadhaar"),
                        pending.get("driving_license"),
                        pending.get("ration_card"),
                        pending.get("vehicle_number"),
                        pending.get("vehicle_image"),
                    ),
                )
                db.commit()
                cursor.execute("SELECT * FROM users WHERE email=%s", (pending["email"],))
                user = cursor.fetchone()
                session["user"] = user["name"]
                session["user_id"] = user["id"]
                session["user_email"] = user["email"]
                session["user_location"] = user.get("location", "Not set")
                session["role"] = user.get("role", "farmer")
                session.pop("pending_registration", None)
                session.pop("otp_sent_to", None)
                return redirect("/profile")
            except mysql.connector.Error:
                error = "Unable to complete registration. Please try again."
        else:
            error = "Invalid OTP. Please double-check the code sent to your phone."

    return render_template(
        "verify_otp.html",
        error=error,
        phone=session.get("otp_sent_to"),
        otp_demo=pending.get("otp"),
    )

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect("/login")
    if session.get("role") == "admin":
        return redirect("/admin")

    profile_photo = None
    if session.get("user_email"):
        cursor.execute("SELECT photo FROM users WHERE email=%s", (session.get("user_email"),))
        profile_data = cursor.fetchone() or {}
        if profile_data.get("photo"):
            profile_photo = f"/static/{profile_data['photo']}"

    return render_template(
        "dashboard.html",
        user_location=session.get("user_location", "Not set"),
        profile_photo=profile_photo,
    )

# ---------------- PROFILE ----------------
@app.route("/profile")
def profile():
    if not session.get("user"):
        return redirect("/login")

    cursor.execute("SELECT * FROM users WHERE email=%s", (session.get("user_email"),))
    profile_data = cursor.fetchone() or {}
    return render_template("profile.html", profile=profile_data)

# ---------------- MACHINERY ----------------
@app.route("/machinery")
def machinery():
    if not session.get("user"):
        return redirect("/login")

    cursor.execute("SELECT * FROM machinery")
    data = cursor.fetchall()
    return render_template("machinery.html", machines=data)

@app.route("/book/<int:id>", methods=["GET", "POST"])
def book(id):
    if not session.get("user"):
        return redirect("/login")

    if request.method == "POST":
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        notes = request.form.get("notes", "")

        cursor.execute("SELECT price_per_day FROM machinery WHERE id = %s", (id,))
        machine = cursor.fetchone()
        if not machine:
            flash("Machine not found", "error")
            return redirect("/machinery")

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1  # inclusive
        total_cost = days * machine["price_per_day"]

        cursor.execute(
            "INSERT INTO bookings(machine_id, user_id, start_date, end_date, total_cost, notes, farmer_location) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (id, session.get("user_id"), start_date, end_date, total_cost, notes, session.get("user_location", "Not set")),
        )
        db.commit()
        flash("Booking request submitted successfully! Waiting for admin approval.", "success")
        return redirect("/bookings")

    cursor.execute("SELECT * FROM machinery WHERE id = %s", (id,))
    machine = cursor.fetchone()
    if not machine:
        flash("Machine not found", "error")
        return redirect("/machinery")

    return render_template("book_machine.html", machine=machine, today=datetime.now().strftime("%Y-%m-%d"))

# ---------------- BOOKINGS ----------------
@app.route("/bookings")
def bookings():
    if not session.get("user"):
        return redirect("/login")

    cursor.execute(
        "SELECT b.id, b.start_date, b.end_date, b.status, b.total_cost, b.notes, b.created_at, b.admin_phone, b.admin_photo, b.admin_vehicle_number, b.admin_location, b.farmer_location, "
        "m.name AS machine_name, m.location AS machine_location, m.price_per_day, m.owner_contact, m.image_url AS machine_image, m.tracking_location AS machine_tracking_location "
        "FROM bookings b "
        "LEFT JOIN machinery m ON b.machine_id = m.id "
        "WHERE b.user_id = %s "
        "ORDER BY b.created_at DESC",
        (session.get("user_id"),),
    )
    data = cursor.fetchall()
    return render_template("bookings.html", bookings=data)

@app.route("/cancel_booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if not session.get("user"):
        return redirect("/login")

    cursor.execute(
        "SELECT status FROM bookings WHERE id = %s AND user_id = %s",
        (booking_id, session.get("user_id"))
    )
    booking = cursor.fetchone()
    if not booking:
        flash("Booking not found", "error")
        return redirect("/bookings")

    if booking["status"] not in ["pending", "approved"]:
        flash("Cannot cancel this booking", "error")
        return redirect("/bookings")

    cursor.execute(
        "UPDATE bookings SET status = 'cancelled' WHERE id = %s",
        (booking_id,)
    )
    db.commit()
    flash("Booking cancelled successfully", "success")
    return redirect("/bookings")

@app.route("/booking/<int:booking_id>/track")
def booking_track(booking_id):
    if not session.get("user"):
        return redirect("/login")

    cursor.execute(
        "SELECT b.*, m.location AS machine_location, u.location AS farmer_location FROM bookings b "
        "LEFT JOIN machinery m ON b.machine_id = m.id "
        "LEFT JOIN users u ON b.user_id = u.id "
        "WHERE b.id = %s AND b.user_id = %s",
        (booking_id, session.get("user_id")),
    )
    booking = cursor.fetchone()
    if not booking or booking.get("status") != "approved":
        flash("Booking directions are available only for approved bookings.", "error")
        return redirect("/bookings")

    origin = booking.get("farmer_location") or session.get("user_location", "")
    destination = booking.get("admin_location") or booking.get("machine_location") or ""
    return render_template(
        "booking_track.html",
        booking=booking,
        origin=origin,
        destination=destination,
        origin_url=quote_plus(origin) if origin else "",
        destination_url=quote_plus(destination) if destination else "",
        google_maps_api_key=GOOGLE_MAPS_API_KEY,
    )

# ---------------- ADMIN BOOKING MANAGEMENT ----------------
@app.route("/admin/bookings")
def admin_bookings():
    if not session.get("user") or session.get("role") != "admin":
        return redirect("/login")

    cursor.execute(
        "SELECT b.id, b.start_date, b.end_date, b.status, b.total_cost, b.notes, b.created_at, b.admin_phone, b.admin_photo, b.admin_vehicle_number, b.admin_location, "
        "m.name AS machine_name, m.location AS machine_location, m.price_per_day, "
        "u.name AS user_name, u.email AS user_email, u.location AS user_location "
        "FROM bookings b "
        "LEFT JOIN machinery m ON b.machine_id = m.id "
        "LEFT JOIN users u ON b.user_id = u.id "
        "ORDER BY b.created_at DESC"
    )
    data = cursor.fetchall()
    return render_template("admin_bookings.html", bookings=data)

@app.route("/admin/approve_booking/<int:booking_id>", methods=["POST"])
def approve_booking(booking_id):
    if not session.get("user") or session.get("role") != "admin":
        return redirect("/login")

    cursor.execute("SELECT * FROM users WHERE id = %s", (session.get("user_id"),))
    admin_user = cursor.fetchone()
    if not admin_user or admin_user.get("role") != "admin":
        flash("Only admins can approve bookings.", "error")
        return redirect("/admin/bookings")

    cursor.execute(
        "UPDATE bookings SET status = 'approved', accepted_by_admin_id = %s, admin_phone = %s, admin_photo = %s, admin_vehicle_number = %s, admin_location = %s WHERE id = %s AND status = 'pending'",
        (
            session.get("user_id"),
            admin_user.get("phone"),
            admin_user.get("photo"),
            admin_user.get("vehicle_number"),
            admin_user.get("location"),
            booking_id,
        )
    )
    if cursor.rowcount == 0:
        flash("This booking is already processed or not found.", "error")
    else:
        db.commit()
        flash("Booking approved successfully", "success")
    return redirect("/admin/bookings")

@app.route("/admin/reject_booking/<int:booking_id>", methods=["POST"])
def reject_booking(booking_id):
    if not session.get("user") or session.get("role") != "admin":
        return redirect("/login")

    cursor.execute(
        "UPDATE bookings SET status = 'rejected' WHERE id = %s AND status = 'pending'",
        (booking_id,)
    )
    if cursor.rowcount == 0:
        flash("This booking is already processed or not found.", "error")
    else:
        db.commit()
        flash("Booking rejected", "success")
    return redirect("/admin/bookings")

# Helper function to generate daily price history for a crop
def generate_price_history(crop_name, base_price=2500):
    """Generate 30 days of simulated daily price data for a crop"""
    from datetime import datetime, timedelta
    import random
    
    history = []
    current_date = datetime.now() - timedelta(days=29)
    current_price = base_price
    
    crop_volatility = {
        "Rice": 0.02,
        "Sugarcane": 0.015,
        "Maize": 0.025,
        "Ragi": 0.02,
        "Cotton": 0.03,
        "Groundnut": 0.02,
    }
    
    volatility = crop_volatility.get(crop_name, 0.02)
    
    for i in range(30):
        change = random.uniform(-volatility, volatility)
        current_price = current_price * (1 + change)
        
        history.append({
            "date": current_date.strftime("%d/%m"),
            "price": round(current_price, 2)
        })
        current_date += timedelta(days=1)
    
    return history

# Indian states and their major districts with sample crops
INDIAN_STATES_DISTRICTS = {
    "Andhra Pradesh": {
        "districts": ["Guntur", "Krishna", "East Godavari", "West Godavari", "Chittoor", "Anantapur", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram"],
        "crops": ["Rice", "Cotton", "Chilli", "Sugarcane", "Groundnut", "Maize"]
    },
    "Arunachal Pradesh": {
        "districts": ["Tawang", "West Kameng", "East Kameng", "Papum Pare", "Kurung Kumey", "Kra Daadi", "Lower Subansiri", "Upper Subansiri", "West Siang", "East Siang", "Siang", "Upper Siang", "Lower Siang", "Lower Dibang Valley", "Dibang Valley", "Anjaw", "Lohit", "Namsai", "Changlang", "Tirap", "Longding"],
        "crops": ["Rice", "Maize", "Wheat", "Millet"]
    },
    "Assam": {
        "districts": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong"],
        "crops": ["Rice", "Tea", "Jute", "Sugarcane", "Potato"]
    },
    "Bihar": {
        "districts": ["Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran"],
        "crops": ["Rice", "Wheat", "Maize", "Sugarcane", "Potato"]
    },
    "Chhattisgarh": {
        "districts": ["Balod", "Baloda Bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", "Bilaspur", "Dantewada", "Dhamtari", "Durg", "Gariaband", "Gaurela-Pendra-Marwahi", "Janjgir-Champa", "Jashpur", "Kabirdham", "Kanker", "Kondagaon", "Korba", "Koriya", "Mahasamund", "Mungeli", "Narayanpur", "Raigarh", "Raipur", "Rajnandgaon", "Sukma", "Surajpur", "Surguja"],
        "crops": ["Rice", "Maize", "Wheat", "Soybean", "Groundnut"]
    },
    "Goa": {
        "districts": ["North Goa", "South Goa"],
        "crops": ["Rice", "Coconut", "Cashew", "Sugarcane", "Banana"]
    },
    "Gujarat": {
        "districts": ["Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Botad", "Chhota Udaipur", "Dahod", "Dang", "Devbhoomi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kheda", "Kutch", "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal", "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad"],
        "crops": ["Cotton", "Groundnut", "Wheat", "Sugarcane", "Rice"]
    },
    "Haryana": {
        "districts": ["Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"],
        "crops": ["Wheat", "Rice", "Sugarcane", "Cotton", "Mustard"]
    },
    "Himachal Pradesh": {
        "districts": ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahaul and Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una"],
        "crops": ["Wheat", "Maize", "Rice", "Apple", "Potato"]
    },
    "Jharkhand": {
        "districts": ["Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum", "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara", "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu", "Ramgarh", "Ranchi", "Sahibganj", "Seraikela Kharsawan", "Simdega", "West Singhbhum"],
        "crops": ["Rice", "Wheat", "Maize", "Ragi", "Potato"]
    },
    "Karnataka": {
        "districts": ["Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban", "Bidar", "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada", "Davangere", "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir"],
        "crops": ["Rice", "Ragi", "Maize", "Sugarcane", "Cotton", "Groundnut"]
    },
    "Kerala": {
        "districts": ["Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"],
        "crops": ["Rice", "Coconut", "Banana", "Rubber", "Tea", "Coffee"]
    },
    "Madhya Pradesh": {
        "districts": ["Agar Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat", "Barwani", "Betul", "Bhind", "Bhopal", "Burhanpur", "Chhatarpur", "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", "Guna", "Gwalior", "Harda", "Hoshangabad", "Indore", "Jabalpur", "Jhabua", "Katni", "Khandwa", "Khargone", "Mandla", "Mandsaur", "Morena", "Narsinghpur", "Neemuch", "Panna", "Raisen", "Rajgarh", "Ratlam", "Rewa", "Sagar", "Satna", "Sehore", "Seoni", "Shahdol", "Shajapur", "Sheopur", "Shivpuri", "Sidhi", "Singrauli", "Tikamgarh", "Ujjain", "Umaria", "Vidisha"],
        "crops": ["Wheat", "Soybean", "Cotton", "Sugarcane", "Rice"]
    },
    "Maharashtra": {
        "districts": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"],
        "crops": ["Sugarcane", "Cotton", "Soybean", "Wheat", "Rice", "Grapes", "Onion"]
    },
    "Manipur": {
        "districts": ["Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West", "Jiribam", "Kakching", "Kamjong", "Kangpokpi", "Noney", "Pherzawl", "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul"],
        "crops": ["Rice", "Maize", "Potato", "Sugarcane"]
    },
    "Meghalaya": {
        "districts": ["East Garo Hills", "East Jaintia Hills", "East Khasi Hills", "North Garo Hills", "Ri Bhoi", "South Garo Hills", "South West Garo Hills", "South West Khasi Hills", "West Garo Hills", "West Jaintia Hills", "West Khasi Hills"],
        "crops": ["Rice", "Maize", "Potato", "Orange", "Pineapple"]
    },
    "Mizoram": {
        "districts": ["Aizawl", "Champhai", "Hnahthial", "Khawzawl", "Kolasib", "Lawngtlai", "Lunglei", "Mamit", "Saiha", "Saitual", "Serchhip"],
        "crops": ["Rice", "Maize", "Chilli", "Ginger"]
    },
    "Nagaland": {
        "districts": ["Chümoukedima", "Dimapur", "Kiphire", "Kohima", "Longleng", "Mokokchung", "Mon", "Niuland", "Noklak", "Peren", "Phek", "Shamator", "Tseminyü", "Tuensang", "Wokha", "Zünheboto"],
        "crops": ["Rice", "Maize", "Soybean", "Chilli"]
    },
    "Odisha": {
        "districts": ["Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"],
        "crops": ["Rice", "Sugarcane", "Groundnut", "Cotton", "Maize"]
    },
    "Punjab": {
        "districts": ["Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Ferozepur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Mansa", "Moga", "Muktsar", "Nawanshahr", "Pathankot", "Patiala", "Rupnagar", "Sahibzada Ajit Singh Nagar", "Sangrur", "Sri Muktsar Sahib", "Tarn Taran"],
        "crops": ["Wheat", "Rice", "Cotton", "Sugarcane", "Maize"]
    },
    "Rajasthan": {
        "districts": ["Ajmer", "Alwar", "Banswara", "Baran", "Barmer", "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaipur", "Jaisalmer", "Jalore", "Jhalawar", "Jhunjhunu", "Jodhpur", "Karauli", "Kota", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Sri Ganganagar", "Tonk", "Udaipur"],
        "crops": ["Wheat", "Mustard", "Cotton", "Sugarcane", "Bajra"]
    },
    "Sikkim": {
        "districts": ["East Sikkim", "North Sikkim", "South Sikkim", "West Sikkim"],
        "crops": ["Rice", "Maize", "Cardamom", "Orange", "Ginger"]
    },
    "Tamil Nadu": {
        "districts": ["Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladurai", "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi", "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"],
        "crops": ["Rice", "Sugarcane", "Cotton", "Groundnut", "Banana"]
    },
    "Telangana": {
        "districts": ["Adilabad", "Bhadradri Kothagudem", "Hyderabad", "Jagtial", "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam", "Kumuram Bheem Asifabad", "Mahabubabad", "Mahabubnagar", "Mancherial", "Medak", "Medchal–Malkajgiri", "Mulugu", "Nagarkurnool", "Nalgonda", "Narayanpet", "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy", "Warangal Rural", "Warangal Urban", "Yadadri Bhuvanagiri"],
        "crops": ["Rice", "Cotton", "Sugarcane", "Maize", "Soybean"]
    },
    "Tripura": {
        "districts": ["Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"],
        "crops": ["Rice", "Pineapple", "Rubber", "Banana"]
    },
    "Uttar Pradesh": {
        "districts": ["Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya", "Azamgarh", "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly", "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj", "Kaushambi", "Kushinagar", "Lakhimpur Kheri", "Lalitpur", "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj", "Raebareli", "Rampur", "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shravasti", "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"],
        "crops": ["Wheat", "Rice", "Sugarcane", "Potato", "Mustard"]
    },
    "Uttarakhand": {
        "districts": ["Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Haridwar", "Nainital", "Pauri Garhwal", "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi"],
        "crops": ["Rice", "Wheat", "Sugarcane", "Potato", "Maize"]
    },
    "West Bengal": {
        "districts": ["Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur", "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur"],
        "crops": ["Rice", "Jute", "Potato", "Sugarcane", "Wheat"]
    },
    # Union Territories
    "Andaman and Nicobar Islands": {
        "districts": ["Nicobar", "North and Middle Andaman", "South Andaman"],
        "crops": ["Rice", "Coconut", "Banana", "Pineapple"]
    },
    "Chandigarh": {
        "districts": ["Chandigarh"],
        "crops": ["Wheat", "Rice", "Sugarcane"]
    },
    "Dadra and Nagar Haveli and Daman and Diu": {
        "districts": ["Dadra and Nagar Haveli", "Daman", "Diu"],
        "crops": ["Rice", "Sugarcane", "Banana", "Mango"]
    },
    "Delhi": {
        "districts": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", "North West Delhi", "Shahdara", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi"],
        "crops": ["Wheat", "Rice", "Sugarcane", "Potato"]
    },
    "Jammu and Kashmir": {
        "districts": ["Anantnag", "Bandipora", "Baramulla", "Budgam", "Doda", "Ganderbal", "Jammu", "Kathua", "Kishtwar", "Kulgam", "Kupwara", "Poonch", "Pulwama", "Rajouri", "Ramban", "Reasi", "Samba", "Shopian", "Srinagar", "Udhampur"],
        "crops": ["Rice", "Wheat", "Maize", "Apple", "Saffron"]
    },
    "Ladakh": {
        "districts": ["Kargil", "Leh"],
        "crops": ["Wheat", "Barley", "Apricot", "Apple"]
    },
    "Lakshadweep": {
        "districts": ["Lakshadweep"],
        "crops": ["Coconut", "Banana", "Vegetables"]
    },
    "Puducherry": {
        "districts": ["Karaikal", "Mahe", "Puducherry", "Yanam"],
        "crops": ["Rice", "Sugarcane", "Banana", "Coconut"]
    }
}

def generate_indian_crop_data():
    """Generate comprehensive crop price data for all Indian states and districts"""
    import random
    
    sample_data = []
    base_date = "21/04/2026"
    
    # Common crops with base prices (₹ per quintal)
    crop_base_prices = {
        "Rice": (1800, 2800),
        "Wheat": (1900, 2500),
        "Maize": (1500, 2000),
        "Sugarcane": (2500, 3500),
        "Cotton": (4800, 6000),
        "Groundnut": (4500, 5500),
        "Soybean": (3000, 4000),
        "Mustard": (4000, 5000),
        "Ragi": (1600, 2200),
        "Bajra": (1400, 1800),
        "Jowar": (1500, 2000),
        "Barley": (1600, 2100),
        "Gram": (3500, 4500),
        "Tur": (4000, 5000),
        "Moong": (5000, 6500),
        "Urad": (4800, 6000),
        "Potato": (800, 1500),
        "Onion": (600, 1200),
        "Tomato": (800, 2000),
        "Banana": (1200, 2500),
        "Mango": (3000, 6000),
        "Orange": (2000, 4000),
        "Apple": (4000, 8000),
        "Grapes": (2500, 5000),
        "Pineapple": (1500, 3000),
        "Coconut": (2000, 3500),
        "Tea": (1000, 2000),
        "Coffee": (15000, 25000),
        "Rubber": (8000, 12000),
        "Jute": (3000, 4000),
        "Chilli": (5000, 15000),
        "Turmeric": (4000, 8000),
        "Ginger": (6000, 10000),
        "Garlic": (3000, 6000),
        "Cardamom": (8000, 15000),
        "Saffron": (50000, 100000),
        "Apricot": (8000, 15000)
    }
    
    for state, state_data in INDIAN_STATES_DISTRICTS.items():
        districts = state_data["districts"]
        crops = state_data["crops"]
        
        # Generate data for 2-3 districts per state to keep data manageable
        selected_districts = districts[:min(3, len(districts))]
        
        for district in selected_districts:
            # Generate data for 2-4 crops per district
            selected_crops = crops[:min(4, len(crops))]
            
            for crop in selected_crops:
                if crop in crop_base_prices:
                    min_price, max_price = crop_base_prices[crop]
                    # Add some regional variation
                    variation = random.uniform(0.8, 1.2)
                    min_price = int(min_price * variation)
                    max_price = int(max_price * variation)
                    modal_price = int((min_price + max_price) / 2)
                    
                    # Generate variety based on crop
                    varieties = {
                        "Rice": ["Basmati", "Ponni", "Sona Masuri", "IR-64", "Swarna"],
                        "Wheat": ["Lokwan", "PBW-343", "HD-2967", "C-306"],
                        "Cotton": ["Bunny", "MCU-5", "H-4", "Suraj"],
                        "Sugarcane": ["CO-86032", "CO-0238", "CO-0118"],
                        "Groundnut": ["TMV-2", "K-6", "TAG-24"],
                        "Maize": ["DHM-117", "Ganga-5", "HQPM-1"],
                        "Soybean": ["JS-335", "JS-9305", "MAUS-71"],
                        "Potato": ["Kufri Jyoti", "Kufri Pukhraj", "Kufri Chipsona-1"],
                        "Banana": ["Poovan", "Robusta", "Grand Naine"],
                        "Grapes": ["Thompson Seedless", "Sonaka", "Sharad Seedless"],
                        "Orange": ["Nagpur", "Mosambi", "Kinnow"],
                        "Apple": ["Red Delicious", "Royal Gala", "Fuji"],
                        "Mango": ["Alphonso", "Dasheri", "Langra"],
                        "Chilli": ["Byadgi", "Guntur", "Kashmiri"],
                        "Turmeric": ["Rajapore", "Alleppy", "Erode"],
                        "Ginger": ["Rio-de-Janeiro", "China", "Maran"],
                        "Garlic": ["G-1", "G-282", "G-41"],
                        "Onion": ["Red", "White", "Pink"],
                        "Tomato": ["Pusa Ruby", "Arka Vikas", "Solan Lalima"],
                        "Coconut": ["Tall", "Dwarf"],
                        "Tea": ["Assam", "Darjeeling", "Nilgiri"],
                        "Coffee": ["Arabica", "Robusta"],
                        "Rubber": ["RRIM-600", "PB-235"],
                        "Jute": ["Deshi", "Tossa"],
                        "Cardamom": ["Malabar", "Mysore"],
                        "Saffron": ["Kashmiri"],
                        "Apricot": ["New Castle", "Stark Early Orange"],
                        "Mustard": ["Pusa Bold", "Varuna"],
                        "Ragi": ["GPU-28", "Indaf-5"],
                        "Bajra": ["HHB-67", "HHB-223"],
                        "Jowar": ["CSH-16", "CSH-22"],
                        "Barley": ["RD-2035", "RD-2552"],
                        "Gram": ["DGG-2", "JG-11"],
                        "Tur": ["LBG-17", "LBG-623"],
                        "Moong": ["Pusa-105", "Pusa Vishal"],
                        "Urad": ["PU-31", "PU-35"],
                        "Pineapple": ["Kew", "Queen"],
                        "Coriander": ["Sudha", "RCR-684"],
                        "Cumin": ["GC-4", "RGC-936"],
                        "Fennel": ["RF-101", "RF-125"]
                    }
                    
                    variety = random.choice(varieties.get(crop, ["FAQ"]))
                    
                    sample_data.append({
                        "state": state,
                        "district": district,
                        "market": f"{district} Market",
                        "commodity": crop,
                        "variety": variety,
                        "grade": "FAQ",
                        "arrival_date": base_date,
                        "min_price": min_price,
                        "max_price": max_price,
                        "modal_price": modal_price
                    })
    
    return sample_data
@app.route("/prices", methods=["GET", "POST"])
def prices():

    if not session.get("user"):
        return redirect("/login?next=/prices")

    error = None
    success = None
    selected_state = request.args.get("state", "")
    selected_district = request.args.get("district", "")
    selected_crop = request.args.get("crop", "")

    # Fetch data from API
    api_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": "579b464db66ec23bdd0000018de3ac3fb1de488a45a7428d7ffc0fb9",  # Replace with your actual API key from data.gov.in
        "format": "json",
        "limit": 1000
    }
    
    try:
        # First, fetch all data to populate dropdowns
        all_response = requests.get(api_url, params=params, timeout=30)
        all_response.raise_for_status()
        all_data = all_response.json()
        all_prices = all_data.get("records", [])
        
        # Add sample data for Karnataka/Mandya if not present in API
        sample_data = generate_indian_crop_data()
        
        # Add sample data to API data
        all_prices.extend(sample_data)
        
        # Get unique values for dropdowns from all data
        states = sorted(set(p.get("state", "") for p in all_prices if p.get("state")))
        
        # Filter districts based on selected state
        if selected_state:
            districts = sorted(set(p.get("district", "") for p in all_prices if p.get("state") == selected_state and p.get("district")))
        else:
            districts = []
            
        # Filter crops based on selected district
        if selected_district:
            crops = sorted(set(p.get("commodity", "") for p in all_prices if p.get("district") == selected_district and p.get("commodity")))
        else:
            crops = []
        
        # Now filter for display if selections are made
        if selected_state or selected_district or selected_crop:
            params["filters[state]"] = selected_state
            params["filters[district]"] = selected_district
            params["filters[commodity]"] = selected_crop
        
            # Fetch filtered data if any filters are applied
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            api_prices = data.get("records", [])
            # Add matching sample data
            sample_prices = [p for p in sample_data if 
                           (not selected_state or p.get("state") == selected_state) and
                           (not selected_district or p.get("district") == selected_district) and
                           (not selected_crop or p.get("commodity") == selected_crop)]
            prices = api_prices + sample_prices
        else:
            prices = all_prices  # Show all prices if no filters
            
    except Exception as e:
        error = f"Unable to fetch crop prices from API: {e}. Showing sample data."
        # Add sample data for Karnataka/Mandya if not present in API
        sample_data = generate_indian_crop_data()
        prices = sample_data
        states = sorted(set(p.get("state", "") for p in sample_data if p.get("state")))
        districts = sorted(set(p.get("district", "") for p in sample_data if p.get("district")))
        crops = sorted(set(p.get("commodity", "") for p in sample_data if p.get("commodity")))

    # Kannada crop name mapping (add more as needed)
    kannada_names = {
        "Rice": "ಅಕ್ಕಿ",
        "Wheat": "ಗೋಧಿ",
        "Maize": "ಮೆಕ್ಕೆಜೋಳ",
        "Sugarcane": "ಕಬ್ಬು",
        "Cotton": "ಹತ್ತಿ",
        "Onion": "ಈರುಳ್ಳಿ",
        "Potato": "ಆಲೂಗಡ್ಡೆ",
        "Tomato": "ಟೊಮೆಟೊ",
        "Brinjal": "ಬದನೇಕಾಯಿ",
        "Cabbage": "ಕೋಸು",
        "Cauliflower": "ಹೂಕೋಸು",
        "Carrot": "ಗಾಜರ್",
        "Green Chilli": "ಹಸಿಮೆಣಸಿನಕಾಯಿ",
        "Red Chilli": "ಕೆಂಪು ಮೆಣಸಿನಕಾಯಿ",
        "Garlic": "ಬೆಳ್ಳುಳ್ಳಿ",
        "Ginger": "ಶುಂಠಿ",
        "Turmeric": "ಅರಿಶಿನ",
        "Coriander": "ಕೊತ್ತಂಬರಿ ಸೊಪ್ಪು",
        "Banana": "ಬಾಳೆಹಣ್ಣು",
        "Mango": "ಮಾವು",
        "Orange": "ಕಿತ್ತಳೆ",
        "Apple": "ಸೇಬು",
        "Grapes": "ದ್ರಾಕ್ಷಿ",
        "Pomegranate": "ದಾಳಿಂಬೆ",
        "Groundnut": "ಕಡಲೆಕಾಯಿ",
        "Soybean": "ಸೋಯಾಬೀನ್",
        "Mustard": "ಸಾಸಿವೆ",
        "Sunflower": "ಸೂರ್ಯಕಾಂತಿ",
        "Jowar": "ಜೋಳ",
        "Bajra": "ಬಜ್ರಾ",
        "Ragi": "ರಾಗಿ",
        "Barley": "ಜವ",
        "Gram": "ಚಣ",
        "Moong": "ಹೆಸರು ಕಾಳು",
        "Urad": "ಉದ್ದಿನ ಬೆಳೆ",
        "Tur": "ತೊಗರಿ",
        "Masoor": "ಮಸೂರ್",
        "Lentil": "ಮಸೂರ್ ದಾಳ್",
        # Crops added for Mandya district
        "Sugarcane": "ಕರಿಬೇವು",
        "Ragi": "ರಾಗಿ",
        "Maize": "ಮೆಕ್ಕೆಜೋಳ",
        "Cotton": "ಹತ್ತಿ",
        "Groundnut": "ಕಡಲೆಕಾಯಿ",
        # Add more mappings as needed
    }

    for p in prices:
        p["kannada_name"] = kannada_names.get(p.get("commodity", ""), p.get("commodity", ""))

    # Generate price history for the selected crop
    price_history = None
    if selected_crop and prices:
        # Get the base price from the first matching crop
        base_price = prices[0].get("modal_price", 2500) if prices else 2500
        price_history = generate_price_history(selected_crop, base_price)

    gov_details = fetch_gov_crop_details()
    return render_template(
        "prices.html",
        prices=prices,
        states=states,
        districts=districts,
        crops=crops,
        selected_state=selected_state,
        selected_district=selected_district,
        selected_crop=selected_crop,
        gov_details=gov_details,
        price_history=price_history,
        error=error,
        success=success,
    )

# ---------------- MAP ----------------
@app.route("/map")
def map_view():
    if not session.get("user"):
        return redirect("/login")

    user_location = session.get("user_location", "Not set")
    user_coords = geocode_location(user_location)
    return render_template(
        "map.html",
        user_location=user_location,
        user_coords=user_coords,
        google_maps_api_key=GOOGLE_MAPS_API_KEY,
    )

# ---------------- MOTOR ----------------
@app.route("/motor")
def motor():
    if not session.get("user"):
        return redirect("/login")
    return render_template("motor.html")

# ---------------- DRONE ----------------
@app.route("/drone")
def drone():
    if not session.get("user"):
        return redirect("/login")
    return render_template("drone.html")

@app.route("/drone/device-info", methods=["GET", "POST"])
def drone_device_info():
    if not session.get("user"):
        return jsonify({"success": False, "message": "Login required"}), 401

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        session["drone_user_name"] = data.get("userName", "")
        session["drone_name"] = data.get("droneName", "")
        session["drone_bt_name"] = data.get("bluetoothName", "")
        return jsonify({
            "success": True,
            "message": "Device info saved",
            "info": {
                "userName": session.get("drone_user_name", ""),
                "droneName": session.get("drone_name", ""),
                "bluetoothName": session.get("drone_bt_name", ""),
            },
        })

    return jsonify({
        "success": True,
        "info": {
            "userName": session.get("drone_user_name", ""),
            "droneName": session.get("drone_name", ""),
            "bluetoothName": session.get("drone_bt_name", ""),
        },
    })

@app.route("/drone/state")
def drone_state():
    if not session.get("user"):
        return jsonify({"success": False, "message": "Login required"}), 401
    return jsonify({"success": True, "state": get_drone_state_for_client()})

@app.route("/drone/command", methods=["POST"])
def drone_command():
    if not session.get("user"):
        return jsonify({"success": False, "message": "Login required"}), 401

    data = request.get_json(silent=True) or {}
    action = data.get("action")
    payload = data.get("payload", {})
    if not action:
        return jsonify({"success": False, "message": "Missing action"}), 400

    update_drone_state()
    timer = threading.Timer(0.7, execute_drone_command, args=(action, payload))
    timer.daemon = True
    timer.start()

    return jsonify({"success": True, "message": f"Command {action} queued", "action": action})

# ---------------- CCTV ----------------
@app.route("/cctv")
def cctv():
    if not session.get("user"):
        return redirect("/login")
    return render_template("cctv.html")

# ---------------- WEATHER ----------------
@app.route("/weather")
def weather():
    if not session.get("user"):
        return redirect("/login")

    weather_data = fetch_openweather(session.get("user_location", "New Delhi,IN"))
    return render_template("weather.html", weather=weather_data)

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if not session.get("user"):
        return redirect("/login")

    cursor.execute("SELECT COUNT(*) AS count FROM users")
    user_count = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) AS count FROM machinery")
    machinery_count = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) AS count FROM crop_prices")
    price_count = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) AS count FROM bookings")
    booking_count = cursor.fetchone()["count"]

    # Get pending bookings count for admin attention
    cursor.execute("SELECT COUNT(*) AS count FROM bookings WHERE status = 'pending'")
    pending_bookings = cursor.fetchone()["count"]

    cursor.execute(
        "SELECT m.name, count(*) AS booking_count FROM bookings b "
        "LEFT JOIN machinery m ON b.machine_id = m.id "
        "GROUP BY m.name ORDER BY booking_count DESC LIMIT 5"
    )
    top_machines = cursor.fetchall()

    return render_template(
        "admin.html",
        user_count=user_count,
        machinery_count=machinery_count,
        price_count=price_count,
        booking_count=booking_count,
        pending_bookings=pending_bookings,
        top_machines=top_machines,
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
