-- ================= DATABASE SETUP =================
-- Run this script in MySQL to create the database and tables
-- Command: mysql -u root -p < setup_database.sql

-- Create database
CREATE DATABASE IF NOT EXISTS missing_person_ai;
USE missing_person_ai;

-- ================= USERS TABLE =================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    mobile VARCHAR(20),
    station_name VARCHAR(255),
    role_name VARCHAR(50) DEFAULT 'Police',
    role_id INT DEFAULT 2,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ================= MISSING PERSONS TABLE =================
CREATE TABLE IF NOT EXISTS missing_persons (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    age INT,
    gender VARCHAR(20),
    last_seen_location VARCHAR(500),
    description TEXT,
    photo_path VARCHAR(500),
    face_encoding LONGTEXT,
    status VARCHAR(50) DEFAULT 'MISSING',
    reporter_name VARCHAR(255),
    reporter_mobile VARCHAR(20),
    last_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_reporter_mobile (reporter_mobile),
    INDEX idx_status (status),
    INDEX idx_person_id (person_id)
);

-- ================= FIR CASES TABLE =================
CREATE TABLE IF NOT EXISTS fir_cases (
    fir_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    incident_type VARCHAR(100) NOT NULL,
    location VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    accused VARCHAR(500),
    delay_reason TEXT,
    property TEXT,
    date VARCHAR(50),
    time VARCHAR(50),
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ================= CAMERA FRAMES TABLE =================
CREATE TABLE IF NOT EXISTS camera_frames (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_path VARCHAR(500) NOT NULL,
    camera_location VARCHAR(255),
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed TINYINT(1) DEFAULT 0,
    INDEX idx_captured_at (captured_at)
);

-- ================= POLICE STATIONS TABLE =================
CREATE TABLE IF NOT EXISTS police_stations (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    station_name VARCHAR(255) UNIQUE NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    contact_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================= INSERT DEFAULT DATA =================

-- Insert sample police stations
INSERT IGNORE INTO police_stations (station_name, city, state, contact_number) VALUES
('Central Police Station', 'Mumbai', 'Maharashtra', '022-1234567'),
('North Police Station', 'Delhi', 'Delhi', '011-2345678'),
('South Police Station', 'Bangalore', 'Karnataka', '080-3456789'),
('East Police Station', 'Kolkata', 'West Bengal', '033-4567890'),
('West Police Station', 'Chennai', 'Tamil Nadu', '044-5678901');

-- ================= VERIFY TABLES =================
SHOW TABLES;

-- ================= TABLE STRUCTURES =================
DESCRIBE users;
DESCRIBE missing_persons;
DESCRIBE fir_cases;
DESCRIBE camera_frames;
DESCRIBE police_stations;

-- ================= SUCCESS MESSAGE =================
SELECT 'Database setup completed successfully!' AS message;
