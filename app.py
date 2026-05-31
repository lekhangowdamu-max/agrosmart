from sqlalchemy import text
import json
import os
from datetime import date, timedelta
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import urlopen

from flask import Flask, flash, redirect, render_template, render_template_string, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

from database import configure_app, db
from location_data import COMMON_CROPS, CROP_KANNADA_NAMES, INDIA_STATE_DISTRICTS, STATE_CROP_OVERRIDES
from models import Booking, CropPrice, DroneLog, DroneTelemetry, Machinery, Upload, User

login_manager = LoginManager()

LOGO_URL = "/static/logo.svg"

load_dotenv()


def merge_sorted(*groups):
    values = []
    seen = set()
    for group in groups:
        for item in group or []:
            if not item:
                continue
            clean_item = str(item).strip()
            key = clean_item.casefold()
            if clean_item and key not in seen:
                values.append(clean_item)
                seen.add(key)
    return sorted(values, key=str.casefold)


def crop_label(crop):
    kannada_name = CROP_KANNADA_NAMES.get(crop)
    return f"{crop} ({kannada_name})" if kannada_name else crop


def google_maps_search_url(query):
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"


def google_maps_directions_url(destination, origin=None):
    url = f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(destination)}&travelmode=driving"
    if origin:
        url += f"&origin={quote_plus(origin)}"
    return url


def google_maps_embed_url(query, api_key):
    if not api_key or api_key == "your_google_maps_api_key":
        return None
    return f"https://www.google.com/maps/embed/v1/place?key={quote_plus(api_key)}&q={quote_plus(query)}"


def fetch_weather(location, api_key):
    if not api_key:
        return {"error": "Weather API key is not configured."}

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={quote_plus(location)}&appid={quote_plus(api_key)}&units=metric"
    )

    try:
        with urlopen(url, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 401:
            return {"error": "Weather API key was rejected by OpenWeatherMap."}
        if error.code == 404:
            return {"error": f"Weather data was not found for {location}."}
        return {"error": "Weather service returned an error. Please try again later."}
    except (URLError, TimeoutError, json.JSONDecodeError):
        return {"error": "Weather service is unavailable. Please try again later."}

    weather = data.get("weather") or [{}]
    main = data.get("main") or {}
    wind = data.get("wind") or {}

    return {
        "location": data.get("name") or location,
        "temperature": round(main.get("temp", 0)),
        "feels_like": round(main.get("feels_like", 0)),
        "description": (weather[0].get("description") or "Current conditions").title(),
        "humidity": main.get("humidity", 0),
        "wind": wind.get("speed", 0),
    }


def market_location_query(market, district, state):
    parts = [market, district, state, "agricultural market India"]
    return ", ".join(part for part in parts if part)


def build_indicative_crop_prices(state, district, crop):
    base_prices = {
        "Arecanut": 36000, "Bajra": 2200, "Banana": 1800, "Barley": 2100, "Black Gram": 7600,
        "Brinjal": 1600, "Cabbage": 1200, "Cardamom": 95000, "Cashew": 9800, "Castor Seed": 6200,
        "Cauliflower": 1500, "Chilli": 13500, "Coconut": 2600, "Coffee": 18500, "Coriander": 7200,
        "Cotton": 6600, "Cucumber": 1300, "Garlic": 9500, "Ginger": 8200, "Gram": 5600,
        "Grapes": 4200, "Green Gram": 7800, "Groundnut": 6200, "Guava": 2400, "Jowar": 3100,
        "Jute": 4800, "Lentil": 6200, "Linseed": 5600, "Maize": 2100, "Mango": 3800,
        "Masur": 6200, "Mustard": 5400, "Onion": 2200, "Orange": 3600, "Paddy": 2300,
        "Pea": 4200, "Pepper": 52000, "Pomegranate": 6800, "Potato": 1600, "Ragi": 3800,
        "Rapeseed": 5400, "Red Gram": 8600, "Rice": 3200, "Rubber": 15000, "Sesamum": 11500,
        "Soybean": 4700, "Sugarcane": 3400, "Sunflower": 6100, "Tea": 21000, "Tobacco": 8800,
        "Tomato": 1800, "Turmeric": 12500, "Wheat": 2400,
    }
    base = base_prices.get(crop, 3500)
    location = district or state or "India"
    seed = sum(ord(char) for char in f"{state}|{district}|{crop}") % 19
    modal = int(base * (0.92 + seed / 100))
    rows = []

    for index, market_name in enumerate([
        f"{location} APMC Market",
        f"{location} Wholesale Market",
        f"{location} Local Mandi",
    ]):
        adjustment = (index - 1) * 85 + seed * 12
        row_modal = max(100, modal + adjustment)
        rows.append(SimpleNamespace(
            commodity=crop,
            kannada_name=CROP_KANNADA_NAMES.get(crop, crop),
            market=market_name,
            min_price=max(50, row_modal - 180),
            max_price=row_modal + 220,
            modal_price=row_modal,
            arrival_date=date.today() - timedelta(days=index),
            is_estimated=True,
        ))

    return rows

print("Flask app starting...")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["GOOGLE_MAPS_API_KEY"] = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    app.config["OPENWEATHER_API_KEY"] = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    configure_app(app)
    print("Environment loaded...")
    print("Connecting to database...")

    try:
        db.init_app(app)
        with app.app_context():
            pass
        print("Database connected successfully")
    except Exception as e:
        print("DATABASE ERROR:", str(e))

    login_manager.init_app(app)
    login_manager.login_view = "login"

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):

        print("SQL ERROR:", error)

        return {
        "database_error": str(error)
    }, 500

    @app.before_request
    def ping_database():
        return None
    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except (TypeError, ValueError):
        return None


@app.context_processor
def inject_user():
    return {
        "user": current_user if current_user.is_authenticated else None,
        "logo_url": LOGO_URL,
        "role": current_user.role if current_user.is_authenticated else None,
    }


@app.route("/")
def home():

    try:

        machine_count = Machinery.query.count()

        crop_count = CropPrice.query.count()

        booking_count = Booking.query.count()

    except Exception as e:

        print("HOME PAGE DB ERROR:", e)

        machine_count = 0
        crop_count = 0
        booking_count = 0

    return render_template(
        "home.html",
        machine_count=machine_count,
        crop_count=crop_count,
        booking_count=booking_count
    )

@app.route("/health")
def health():

    return {
        "status": "running",
        "database_uri_exists": bool(
            app.config.get(
                "SQLALCHEMY_DATABASE_URI"
            )
        )
    }, 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html", error="Email and password are required.")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))

        flash("Invalid email or password", "error")
        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html", error=None)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "farmer")
        phone = request.form.get("phone")
        location = request.form.get("location")

        if not name or not email or not password:
            flash("Name, email, and password are required.", "error")
            return render_template("register.html", error="All fields are required")

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role if role in ["farmer", "admin"] else "farmer",
            phone=phone,
            location=location,
        )

        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            db.session.rollback()
            flash("Email already registered", "error")
            return render_template("register.html", error="Email already registered")
        except SQLAlchemyError:
            db.session.rollback()
            flash("Unable to register user at this time.", "error")
            return render_template("register.html", error="Unable to register user at this time.")

    return render_template("register.html", error=None)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    profile_photo = current_user.photo if current_user.photo else None
    return render_template("dashboard.html", user_location=current_user.location or "Not set", profile_photo=profile_photo)


@app.route("/bookings")
@login_required
def bookings():
    from models import Booking, Machinery
    
    user_bookings = db.session.query(Booking, Machinery).join(Machinery).filter(
        Booking.user_id == current_user.id
    ).order_by(Booking.created_at.desc()).all()
    
    # Format bookings for template
    formatted_bookings = []
    for booking, machine in user_bookings:
        formatted_bookings.append({
            'id': booking.id,
            'machine_name': machine.name,
            'machine_image': machine.image_url,
            'machine_location': machine.location,
            'start_date': booking.start_date.strftime('%Y-%m-%d') if booking.start_date else 'N/A',
            'end_date': booking.end_date.strftime('%Y-%m-%d') if booking.end_date else 'N/A',
            'total_cost': booking.total_cost or 0,
            'status': booking.status,
            'created_at': booking.created_at,
            'notes': booking.notes,
            'admin_phone': booking.admin_phone,
            'admin_vehicle_number': booking.admin_vehicle_number,
            'admin_photo': booking.admin_photo,
            'admin_location': booking.admin_location,
        })
    
    return render_template("bookings.html", bookings=formatted_bookings)


@app.route("/machinery")
def machinery():
    machines = Machinery.query.all()
    return render_template("machinery.html", machines=machines)


@app.route("/machinery/<int:machine_id>")
def machinery_detail(machine_id):
    machine = Machinery.query.get_or_404(machine_id)
    return render_template("book_machine.html", machine=machine)


@app.route("/book_machine/<int:machine_id>", methods=["GET", "POST"])
@login_required
def book_machine(machine_id):
    from models import Booking, Machinery
    from datetime import datetime
    
    machine = Machinery.query.get_or_404(machine_id)
    today = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == "POST":
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        notes = request.form.get("notes", "")
        
        if not start_date or not end_date:
            flash("Please select both start and end dates.", "error")
            return redirect(url_for("book_machine", machine_id=machine_id))
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start >= end:
                flash("End date must be after start date.", "error")
                return redirect(url_for("book_machine", machine_id=machine_id))
            
            if start < datetime.now().date():
                flash("Start date cannot be in the past.", "error")
                return redirect(url_for("book_machine", machine_id=machine_id))
            
            # Calculate total cost
            days = (end - start).days + 1
            total_cost = days * (machine.price_per_day or 0)
            
            # Create booking
            booking = Booking(
                machine_id=machine_id,
                user_id=current_user.id,
                start_date=start,
                end_date=end,
                total_cost=total_cost,
                notes=notes,
                farmer_location=current_user.location,
                status='pending'
            )
            
            db.session.add(booking)
            db.session.commit()
            
            flash(f"Booking request submitted successfully! Total cost: ₹{total_cost}", "success")
            return redirect(url_for("bookings"))
            
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for("book_machine", machine_id=machine_id))
    
    return render_template("book_machine.html", machine=machine, today=today)


@app.route("/cancel_booking/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    from models import Booking
    
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()
    
    if booking.status in ['pending', 'approved']:
        booking.status = 'cancelled'
        db.session.commit()
        flash("Booking cancelled successfully.", "success")
    else:
        flash("Cannot cancel this booking.", "error")
    
    return redirect(url_for("bookings"))


@app.route("/booking/<int:booking_id>/track")
@login_required
def track_booking(booking_id):
    from models import Booking, Machinery
    
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()
    machine = Machinery.query.get(booking.machine_id)
    
    return render_template("booking_track.html", booking=booking, machine=machine)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", profile=current_user, edit=False)


@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()
        
        if not name or not email:
            flash("Name and email are required.", "error")
            return redirect(url_for("edit_profile"))
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            flash("Email already registered.", "error")
            return redirect(url_for("edit_profile"))
        
        # Update user
        current_user.name = name
        current_user.email = email
        current_user.phone = phone
        current_user.location = location
        
        # Handle file upload for profile photo
        if 'photo' in request.files:
            photo_file = request.files['photo']

    if photo_file and photo_file.filename:

        upload_folder = os.path.join(
            app.root_path,
            "static",
            "profiles"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        filename = (
            f"user_{current_user.id}_"
            f"{photo_file.filename}"
        )

        save_path = os.path.join(
            upload_folder,
            filename
        )

        photo_file.save(save_path)

        current_user.photo = (
            f"profiles/{filename}"
        )
        
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))
    
    return render_template("profile.html", profile=current_user, edit=True)


@app.route("/admin")
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("dashboard"))
    
    from models import Booking, Machinery, User, CropPrice
    from sqlalchemy import func
    
    # Get statistics
    user_count = User.query.count()
    machinery_count = Machinery.query.count()
    price_count = CropPrice.query.count()
    booking_count = Booking.query.count()
    pending_bookings_count = Booking.query.filter_by(status='pending').count()
    
    # Get top booked machines
    top_machines = db.session.query(
        Machinery.name.label('machine_name'),
        func.count(Booking.id).label('booking_count')
    ).join(Booking).group_by(Machinery.id).order_by(func.count(Booking.id).desc()).limit(5).all()
    
    # Get all pending bookings with user and machine info
    pending_bookings = db.session.query(Booking, User, Machinery).join(User).join(Machinery).filter(
        Booking.status == 'pending'
    ).order_by(Booking.created_at.desc()).all()
    
    # Get approved bookings for tracking
    approved_bookings = db.session.query(Booking, User, Machinery).join(User).join(Machinery).filter(
        Booking.status == 'approved'
    ).order_by(Booking.created_at.desc()).all()
    
    return render_template("admin.html", 
                         user_count=user_count,
                         machinery_count=machinery_count,
                         price_count=price_count,
                         booking_count=booking_count,
                         pending_bookings=pending_bookings_count,
                         top_machines=top_machines,
                         pending_bookings_list=pending_bookings, 
                         approved_bookings=approved_bookings)


@app.route("/admin/booking/<int:booking_id>/<action>", methods=["POST"])
@login_required
def admin_booking_action(booking_id, action):
    if current_user.role != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for("dashboard"))
    
    from models import Booking
    
    booking = Booking.query.get_or_404(booking_id)
    
    if action == 'approve':
        # Get admin details from form
        admin_phone = request.form.get("admin_phone")
        admin_vehicle_number = request.form.get("admin_vehicle_number")
        admin_location = request.form.get("admin_location")
        
        booking.status = 'approved'
        booking.admin_phone = admin_phone
        booking.admin_vehicle_number = admin_vehicle_number
        booking.admin_location = admin_location
        booking.accepted_by_admin_id = current_user.id
        booking.admin_photo = current_user.photo
        
        flash("Booking approved successfully!", "success")
        
    elif action == 'reject':
        booking.status = 'rejected'
        flash("Booking rejected.", "success")
    
    db.session.commit()
    return redirect(url_for("admin_panel"))


@app.route("/admin/bookings")
@login_required
def admin_bookings():
    if current_user.role != 'admin':
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("dashboard"))
    
    from models import Booking, Machinery, User
    
    # Get all bookings with user and machine info
    all_bookings = db.session.query(Booking, User, Machinery).join(User).join(Machinery).order_by(
        Booking.created_at.desc()
    ).all()
    
    # Format for template
    formatted_bookings = []
    for booking, user, machine in all_bookings:
        formatted_bookings.append({
            'id': booking.id,
            'machine_name': machine.name,
            'machine_location': machine.location,
            'user_name': user.name,
            'user_email': user.email,
            'user_location': user.location,
            'start_date': booking.start_date.strftime('%Y-%m-%d') if booking.start_date else 'N/A',
            'end_date': booking.end_date.strftime('%Y-%m-%d') if booking.end_date else 'N/A',
            'total_cost': booking.total_cost or 0,
            'status': booking.status,
            'created_at': booking.created_at,
            'notes': booking.notes,
        })
    
    return render_template("admin_bookings.html", bookings=formatted_bookings)


@app.route("/admin/approve_booking/<int:booking_id>", methods=["POST"])
@login_required
def admin_approve_booking(booking_id):
    if current_user.role != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for("dashboard"))
    
    from models import Booking
    
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'approved'
    booking.accepted_by_admin_id = current_user.id
    db.session.commit()
    
    flash("Booking approved successfully!", "success")
    return redirect(url_for("admin_bookings"))


@app.route("/admin/reject_booking/<int:booking_id>", methods=["POST"])
@login_required
def admin_reject_booking(booking_id):
    if current_user.role != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for("dashboard"))
    
    from models import Booking
    
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'rejected'
    db.session.commit()
    
    flash("Booking rejected.", "success")
    return redirect(url_for("admin_bookings"))


@app.route("/prices", methods=["GET", "POST"])
def prices():
    from models import CropPrice
    
    # Get filter parameters
    selected_state = request.args.get('state', '')
    selected_district = request.args.get('district', '')
    selected_crop = request.args.get('crop', '')
    
    db_states = [
        state
        for (state,) in db.session.query(CropPrice.state)
        .distinct()
        .filter(CropPrice.state.isnot(None))
        .all()
    ]
    states = merge_sorted(INDIA_STATE_DISTRICTS.keys(), db_states)

    db_district_map = {}
    for state, district in (
        db.session.query(CropPrice.state, CropPrice.district)
        .distinct()
        .filter(CropPrice.state.isnot(None), CropPrice.district.isnot(None))
        .all()
    ):
        db_district_map.setdefault(state, []).append(district)

    db_crop_map = {}
    for state, crop in (
        db.session.query(CropPrice.state, CropPrice.commodity)
        .distinct()
        .filter(CropPrice.state.isnot(None), CropPrice.commodity.isnot(None))
        .all()
    ):
        db_crop_map.setdefault(state, []).append(crop)

    district_options = {
        state: merge_sorted(INDIA_STATE_DISTRICTS.get(state, []), db_district_map.get(state, []))
        for state in states
    }
    crop_options = {
        state: merge_sorted(STATE_CROP_OVERRIDES.get(state, COMMON_CROPS), db_crop_map.get(state, []))
        for state in states
    }

    districts = []
    if selected_state:
        districts = district_options.get(selected_state, [])

    crop_query = db.session.query(CropPrice.commodity).distinct().filter(CropPrice.commodity.isnot(None))
    if selected_state:
        crop_query = crop_query.filter(CropPrice.state == selected_state)
    if selected_district:
        crop_query = crop_query.filter(CropPrice.district == selected_district)
    db_crops = [crop for (crop,) in crop_query.all()]
    fallback_crops = crop_options.get(selected_state, COMMON_CROPS) if selected_state else COMMON_CROPS
    crops = merge_sorted(fallback_crops, db_crops)
    
    # Filter prices based on selections
    query = CropPrice.query
    
    if selected_state:
        query = query.filter(CropPrice.state == selected_state)
    if selected_district:
        query = query.filter(CropPrice.district == selected_district)
    if selected_crop:
        query = query.filter(CropPrice.commodity == selected_crop)
    
    prices = query.order_by(CropPrice.arrival_date.desc()).limit(50).all()
    using_indicative_prices = False

    if selected_crop and not prices:
        prices = build_indicative_crop_prices(selected_state, selected_district, selected_crop)
        using_indicative_prices = True
    
    for price in prices:
        price.kannada_name = CROP_KANNADA_NAMES.get(price.commodity, price.commodity)
        if not hasattr(price, "is_estimated"):
            price.is_estimated = False
        price.location_query = market_location_query(price.market, selected_district, selected_state)
        price.google_maps_url = google_maps_search_url(price.location_query)
        price.google_directions_url = google_maps_directions_url(price.location_query)

    selected_crop_details = None
    if selected_crop:
        modal_values = [price.modal_price for price in prices if price.modal_price is not None]
        min_values = [price.min_price for price in prices if price.min_price is not None]
        max_values = [price.max_price for price in prices if price.max_price is not None]
        markets = merge_sorted([price.market for price in prices if price.market])
        map_query = market_location_query(markets[0] if markets else selected_crop, selected_district, selected_state)
        selected_crop_details = {
            "crop": selected_crop,
            "kannada_name": CROP_KANNADA_NAMES.get(selected_crop, "Kannada name not available"),
            "state": selected_state or "All states",
            "district": selected_district or "All districts",
            "record_count": len(prices),
            "market_count": len(markets),
            "markets": markets[:8],
            "min_price": min(min_values) if min_values else None,
            "max_price": max(max_values) if max_values else None,
            "modal_min": min(modal_values) if modal_values else None,
            "modal_max": max(modal_values) if modal_values else None,
            "is_estimated": using_indicative_prices,
            "map_query": map_query,
            "google_maps_url": google_maps_search_url(map_query),
            "google_directions_url": google_maps_directions_url(map_query),
            "google_maps_embed_url": google_maps_embed_url(map_query, app.config.get("GOOGLE_MAPS_API_KEY", "")),
        }
    
    # Get price history for chart (last 30 days)
    price_history = None
    if selected_crop and selected_district:
        history_query = db.session.query(CropPrice.arrival_date, CropPrice.modal_price).filter(
            CropPrice.commodity == selected_crop,
            CropPrice.district == selected_district
        ).order_by(CropPrice.arrival_date.desc()).limit(30).all()
        
        if history_query:
            price_history = {
                'dates': [str(h[0]) for h in reversed(history_query)],
                'prices': [h[1] for h in reversed(history_query)]
            }
    if selected_crop and not price_history and prices:
        ordered_prices = list(reversed(prices[:3]))
        price_history = {
            "dates": [str(price.arrival_date) for price in ordered_prices],
            "prices": [price.modal_price for price in ordered_prices],
        }
    
    return render_template(
        "prices.html",
        prices=prices,
        states=states,
        districts=districts,
        crops=crops,
        selected_state=selected_state,
        selected_district=selected_district,
        selected_crop=selected_crop,
        district_options=district_options,
        crop_options=crop_options,
        common_crops=COMMON_CROPS,
        crop_labels={crop: crop_label(crop) for crop in merge_sorted(COMMON_CROPS, CROP_KANNADA_NAMES.keys(), *crop_options.values())},
        selected_crop_details=selected_crop_details,
        gov_details=[],
        price_history=price_history,
        error=None,
        success=None,
    )


@app.route("/map")
def map_view():
    user_location = "Not set"
    user_coords = None
    
    if current_user.is_authenticated and current_user.location:
        user_location = current_user.location
        # Try to get coordinates from location (simplified - in real app would use geocoding API)
        location_coords = {
            "Bangalore": [12.9716, 77.5946],
            "Mysore": [12.2958, 76.6394],
            "Hubli": [15.3647, 75.1240],
            "Belgaum": [15.8497, 74.4977],
            "Gulbarga": [17.3297, 76.8343],
            "Raichur": [16.2120, 77.3439],
            "Davangere": [14.4644, 75.9218],
            "Shimoga": [13.9299, 75.5681],
        }
        user_coords = location_coords.get(user_location)
    
    return render_template("map.html", user_location=user_location, user_coords=user_coords)


@app.route("/weather")
def weather():
    location = "Bangalore,IN"
    if current_user.is_authenticated and current_user.location:
        location = current_user.location

    openweather_api_key = app.config.get("OPENWEATHER_API_KEY", "")
    weather_data = fetch_weather(location, openweather_api_key)
    return render_template(
        "weather.html",
        weather=weather_data,
        openweather_api_key=openweather_api_key,
    )


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
# - External API calls
# - AI modules
# - Drone modules
# - Heavy imports
# - Background services


if __name__ == "__main__":
    app.run(debug=True)
