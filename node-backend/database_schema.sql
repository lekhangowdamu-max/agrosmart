-- AgroSmart Database Schema (MySQL)
-- This schema is compatible with the Node.js + Express backend

CREATE DATABASE IF NOT EXISTS agrosmart;
USE agrosmart;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('farmer', 'admin') DEFAULT 'farmer',
    phone VARCHAR(20),
    location VARCHAR(150),
    phone_verified TINYINT(1) DEFAULT 0,
    photo VARCHAR(255),
    aadhaar VARCHAR(50),
    driving_license VARCHAR(100),
    ration_card VARCHAR(100),
    vehicle_number VARCHAR(100),
    vehicle_image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Machinery Table
CREATE TABLE IF NOT EXISTS machinery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(150),
    price_per_day INT,
    owner_contact VARCHAR(20),
    image_url VARCHAR(255),
    tracking_location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_location (location),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    machine_id INT NOT NULL,
    user_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'cancelled', 'completed') DEFAULT 'pending',
    total_cost DECIMAL(10, 2),
    notes TEXT,
    farmer_location VARCHAR(150),
    accepted_by_admin_id INT,
    admin_phone VARCHAR(20),
    admin_photo VARCHAR(255),
    admin_vehicle_number VARCHAR(100),
    admin_location VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machinery(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (accepted_by_admin_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_machine_id (machine_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crop Prices Table
CREATE TABLE IF NOT EXISTS crop_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(150),
    district VARCHAR(150),
    market VARCHAR(255),
    commodity VARCHAR(150),
    variety VARCHAR(150),
    grade VARCHAR(100),
    arrival_date DATE,
    min_price INT,
    max_price INT,
    modal_price INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_state (state),
    INDEX idx_district (district),
    INDEX idx_commodity (commodity),
    INDEX idx_arrival_date (arrival_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Uploads Table
CREATE TABLE IF NOT EXISTS uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    filename VARCHAR(255) NOT NULL,
    url VARCHAR(1024) NOT NULL,
    storage_provider VARCHAR(64) DEFAULT 'local',
    content_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Drone Telemetry Table
CREATE TABLE IF NOT EXISTS drone_telemetry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drone_id VARCHAR(100) DEFAULT 'agro-drone-001',
    status VARCHAR(100),
    battery FLOAT,
    altitude FLOAT,
    speed FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    heading FLOAT,
    signal FLOAT,
    mode VARCHAR(100),
    last_command VARCHAR(255),
    waypoint_latitude FLOAT,
    waypoint_longitude FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_drone_id (drone_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Drone Logs Table
CREATE TABLE IF NOT EXISTS drone_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drone_id VARCHAR(100) DEFAULT 'agro-drone-001',
    event TEXT NOT NULL,
    level VARCHAR(50) DEFAULT 'info',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_drone_id (drone_id),
    INDEX idx_level (level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample data for testing
-- Insert sample users
INSERT INTO users (name, email, password, role, phone, location) VALUES
('Admin User', 'admin@agrosmart.com', '$2a$10$example_hash_admin', 'admin', '9999999999', 'Bangalore'),
('Farmer User', 'farmer@agrosmart.com', '$2a$10$example_hash_farmer', 'farmer', '9999999998', 'Mysore');

-- Insert sample machinery
INSERT INTO machinery (name, location, price_per_day, owner_contact, image_url) VALUES
('Tractor', 'Bangalore', 500, '9999999997', '/static/machinery/tractor.jpg'),
('Harvester', 'Mysore', 800, '9999999996', '/static/machinery/harvester.jpg'),
('Plow', 'Belgaum', 300, '9999999995', '/static/machinery/plow.jpg'),
('Thresher', 'Hubli', 400, '9999999994', '/static/machinery/thresher.jpg'),
('Sprayer', 'Davangere', 200, '9999999993', '/static/machinery/sprayer.jpg');

-- Insert sample crop prices
INSERT INTO crop_prices (state, district, market, commodity, variety, grade, arrival_date, min_price, max_price, modal_price) VALUES
('Karnataka', 'Bangalore', 'Bangalore Market', 'Rice', 'Basmati', 'A', CURDATE(), 2000, 2500, 2200),
('Karnataka', 'Bangalore', 'Bangalore Market', 'Wheat', 'Local', 'A', CURDATE(), 1800, 2200, 2000),
('Karnataka', 'Mysore', 'Mysore Market', 'Maize', 'Local', 'A', CURDATE(), 1200, 1500, 1300);
