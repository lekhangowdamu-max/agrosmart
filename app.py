from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "AgroSmart Flask Deployment Working"

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