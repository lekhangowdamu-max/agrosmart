CREATE DATABASE agrosmart;
USE agrosmart;

CREATE TABLE users (
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
);

CREATE TABLE machinery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100),
    price_per_day INT,
    owner_contact VARCHAR(15),
    image_url VARCHAR(255),
    tracking_location VARCHAR(255)
);

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
);

CREATE TABLE crop_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100),
    market_name VARCHAR(100),
    price INT,
    location VARCHAR(100),
    date DATE
);