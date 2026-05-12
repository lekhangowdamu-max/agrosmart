import os
import sqlite3
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app import app
from models import db, User, Machinery, Booking, CropPrice, Upload, DroneTelemetry, DroneLog

SQLITE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agrosmart.db')

TABLES_TO_MIGRATE = [
    'users',
    'machinery',
    'bookings',
    'crop_prices',
    'uploads',
    'drone_telemetry',
    'drone_logs',
]


def get_sqlite_conn():
    if not os.path.exists(SQLITE_FILE):
        return None
    return sqlite3.connect(SQLITE_FILE)


def table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def migrate_users(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, password, role, phone, location, photo, aadhaar, driving_license, ration_card, vehicle_number, vehicle_image FROM users')
    rows = cursor.fetchall()
    count = 0

    for row in rows:
        id_, name, email, password, role, phone, location, photo, aadhaar, driving_license, ration_card, vehicle_number, vehicle_image = row
        if User.query.filter_by(email=email).first():
            continue
        user = User(
            id=id_,
            name=name,
            email=email,
            password=password,
            role=role or 'farmer',
            phone=phone,
            location=location,
            photo=photo,
            aadhaar=aadhaar,
            driving_license=driving_license,
            ration_card=ration_card,
            vehicle_number=vehicle_number,
            vehicle_image=vehicle_image,
        )
        db.session.add(user)
        count += 1
    db.session.commit()
    return count


def migrate_table_generic(conn, table_name, columns, model_class, field_map=None):
    cursor = conn.cursor()
    cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
    rows = cursor.fetchall()
    inserted = 0

    for row in rows:
        data = dict(zip(columns, row))
        if field_map:
            data = {target: data[source] for source, target in field_map.items() if source in data}
        instance = model_class(**data)
        db.session.add(instance)
        inserted += 1
    db.session.commit()
    return inserted


def migrate():
    conn = get_sqlite_conn()
    if conn is None:
        print('No local SQLite file found. Nothing to migrate.')
        return

    with app.app_context():
        db.create_all()

        total = 0
        if table_exists(conn, 'users'):
            print('Migrating users...')
            total += migrate_users(conn)

        if table_exists(conn, 'machinery'):
            print('Migrating machinery...')
            total += migrate_table_generic(
                conn,
                'machinery',
                ['id', 'name', 'location', 'price_per_day', 'owner_contact', 'image_url', 'tracking_location'],
                Machinery
            )

        if table_exists(conn, 'bookings'):
            print('Migrating bookings...')
            total += migrate_table_generic(
                conn,
                'bookings',
                ['id', 'machine_id', 'user_id', 'start_date', 'end_date', 'status', 'total_cost', 'notes', 'farmer_location', 'accepted_by_admin_id', 'admin_phone', 'admin_photo', 'admin_vehicle_number', 'admin_location'],
                Booking
            )

        if table_exists(conn, 'crop_prices'):
            print('Migrating crop prices...')
            total += migrate_table_generic(
                conn,
                'crop_prices',
                ['id', 'state', 'district', 'market', 'commodity', 'variety', 'grade', 'arrival_date', 'min_price', 'max_price', 'modal_price'],
                CropPrice
            )

        if table_exists(conn, 'uploads'):
            print('Migrating uploads...')
            total += migrate_table_generic(
                conn,
                'uploads',
                ['id', 'user_id', 'filename', 'url', 'storage_provider', 'content_type'],
                Upload
            )

        if table_exists(conn, 'drone_telemetry'):
            print('Migrating drone telemetry...')
            total += migrate_table_generic(
                conn,
                'drone_telemetry',
                ['id', 'drone_id', 'status', 'battery', 'altitude', 'speed', 'latitude', 'longitude', 'heading', 'signal', 'mode', 'last_command', 'waypoint_latitude', 'waypoint_longitude'],
                DroneTelemetry
            )

        if table_exists(conn, 'drone_logs'):
            print('Migrating drone logs...')
            total += migrate_table_generic(
                conn,
                'drone_logs',
                ['id', 'drone_id', 'event', 'level'],
                DroneLog
            )

        print(f'Migration complete. {total} records imported.')


if __name__ == '__main__':
    try:
        migrate()
    except SQLAlchemyError as exc:
        print('Migration error:', exc)
        db.session.rollback()
