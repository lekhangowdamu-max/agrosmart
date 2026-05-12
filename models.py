from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy database connection object
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='farmer')
    phone = db.Column(db.String(20))
    location = db.Column(db.String(150))
    phone_verified = db.Column(db.Boolean, default=False)
    photo = db.Column(db.String(255))
    aadhaar = db.Column(db.String(50))
    driving_license = db.Column(db.String(100))
    ration_card = db.Column(db.String(100))
    vehicle_number = db.Column(db.String(100))
    vehicle_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    uploads = db.relationship('Upload', backref='user', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Machinery(db.Model):
    __tablename__ = 'machinery'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=True)
    price_per_day = db.Column(db.Integer, nullable=True)
    owner_contact = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    tracking_location = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = db.relationship('Booking', backref='machine', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machinery.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending')
    total_cost = db.Column(db.Numeric(10, 2), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    farmer_location = db.Column(db.String(150), nullable=True)
    accepted_by_admin_id = db.Column(db.Integer, nullable=True)
    admin_phone = db.Column(db.String(20), nullable=True)
    admin_photo = db.Column(db.String(255), nullable=True)
    admin_vehicle_number = db.Column(db.String(100), nullable=True)
    admin_location = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CropPrice(db.Model):
    __tablename__ = 'crop_prices'

    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(150), nullable=True)
    district = db.Column(db.String(150), nullable=True)
    market = db.Column(db.String(255), nullable=True)
    commodity = db.Column(db.String(150), nullable=True)
    variety = db.Column(db.String(150), nullable=True)
    grade = db.Column(db.String(100), nullable=True)
    arrival_date = db.Column(db.Date, nullable=True)
    min_price = db.Column(db.Integer, nullable=True)
    max_price = db.Column(db.Integer, nullable=True)
    modal_price = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Upload(db.Model):
    __tablename__ = 'uploads'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(1024), nullable=False)
    storage_provider = db.Column(db.String(64), nullable=False, default='local')
    content_type = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DroneTelemetry(db.Model):
    __tablename__ = 'drone_telemetry'

    id = db.Column(db.Integer, primary_key=True)
    drone_id = db.Column(db.String(100), nullable=False, default='agro-drone-001')
    status = db.Column(db.String(100), nullable=True)
    battery = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    speed = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    heading = db.Column(db.Float, nullable=True)
    signal = db.Column(db.Float, nullable=True)
    mode = db.Column(db.String(100), nullable=True)
    last_command = db.Column(db.String(255), nullable=True)
    waypoint_latitude = db.Column(db.Float, nullable=True)
    waypoint_longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DroneLog(db.Model):
    __tablename__ = 'drone_logs'

    id = db.Column(db.Integer, primary_key=True)
    drone_id = db.Column(db.String(100), nullable=False, default='agro-drone-001')
    event = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(50), nullable=True, default='info')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
