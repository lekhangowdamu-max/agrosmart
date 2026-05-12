from flask import Flask, render_template

app = Flask(__name__)

LOGO_URL = "/static/logo.svg"

@app.context_processor
def inject_user():
    return {
        "user": None,  # Disabled authentication
        "logo_url": LOGO_URL,
        "role": None,
    }

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html", error=None)

@app.route("/register")
def register():
    return render_template("register.html", error=None)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", user_location="Not set")

@app.route("/machinery")
def machinery():
    return render_template("machinery.html", machines=[])

@app.route("/prices")
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