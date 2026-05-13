import os

from flask import Flask, flash, redirect, render_template, render_template_string, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from database import configure_app, db
from models import Booking, CropPrice, DroneLog, DroneTelemetry, Machinery, Upload, User

login_manager = LoginManager()

LOGO_URL = "/static/logo.svg"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    configure_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        app.logger.error("Database error: %s", error)
        return render_template_string(
            "<h1>Service unavailable</h1>"
            "<p>We are unable to reach the database right now. Please try again later.</p>"
        ), 503

    @app.before_request
    def ping_database():
        database_url = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if database_url.startswith("postgresql://"):
            try:
                db.session.execute("SELECT 1")
            except OperationalError as exc:
                app.logger.warning("Database connection ping failed: %s", exc)
                db.session.rollback()
                return render_template_string(
                    "<h1>Service unavailable</h1>"
                    "<p>Database connection temporarily unavailable.</p>"
                ), 503

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
    return render_template("home.html")


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
    return render_template("dashboard.html", user_location=current_user.location or "Not set")


@app.route("/machinery")
def machinery():
    machines = Machinery.query.all()
    return render_template("machinery.html", machines=machines)


@app.route("/prices", methods=["GET", "POST"])
def prices():
    return render_template(
        "prices.html",
        prices=[],
        states=[],
        districts=[],
        crops=[],
        selected_state="",
        selected_district="",
        selected_crop="",
        gov_details=[],
        price_history=None,
        error=None,
        success=None,
    )


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
# - External API calls
# - AI modules
# - Drone modules
# - Heavy imports
# - Background services


if __name__ == "__main__":
    app.run(debug=True)
