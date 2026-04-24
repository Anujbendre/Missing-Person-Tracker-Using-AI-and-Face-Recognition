-- ================= ADDITIONAL FEATURES DATABASE SETUP =================
-- Run this script AFTER setup_database.sql to add new feature tables
-- Command: mysql -u root -p missing_person_ai < add_features_tables.sql

USE missing_person_ai;

-- ================= FEATURE 2: DETECTION ALERTS =================
CREATE TABLE IF NOT EXISTS detection_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT,
    frame_id INT,
    confidence FLOAT,
    alert_message TEXT,
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES missing_persons(person_id) ON DELETE SET NULL,
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
);

-- ================= FEATURE 3: CASE STATUS HISTORY =================
CREATE TABLE IF NOT EXISTS case_status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    note TEXT,
    updated_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES missing_persons(person_id) ON DELETE CASCADE,
    INDEX idx_person_id (person_id),
    INDEX idx_created_at (created_at)
);

-- ================= FEATURE 4: CCTV CAMERAS =================
CREATE TABLE IF NOT EXISTS cctv_cameras (
    camera_id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status)
);

-- ================= FEATURE 9: DETECTION LOGS =================
CREATE TABLE IF NOT EXISTS detection_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    image_path VARCHAR(500),
    matched_person_id INT,
    matched_name VARCHAR(255),
    confidence FLOAT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matched_person_id) REFERENCES missing_persons(person_id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- ================= FEATURE 10: CITIZEN USERS =================
-- Add citizen role to users table (already exists, just documenting)
-- role_id = 1: Citizen
-- role_id = 2: Police
-- role_id = 3: Admin

-- ================= INSERT SAMPLE DATA =================

-- Sample CCTV Cameras
INSERT IGNORE INTO cctv_cameras (location_name, latitude, longitude, status) VALUES
('Main Street Junction', 18.5204, 73.8567, 'ACTIVE'),
('Railway Station Entrance', 18.5285, 73.8742, 'ACTIVE'),
('Shopping Mall Parking', 18.5156, 73.8553, 'ACTIVE'),
('City Center Plaza', 18.5236, 73.8478, 'MAINTENANCE'),
('Bus Stand Terminal', 18.5314, 73.8632, 'ACTIVE');

-- ================= VERIFY TABLES =================
SHOW TABLES;

-- ================= TABLE STRUCTURES =================
DESCRIBE detection_alerts;
DESCRIBE case_status_history;
DESCRIBE cctv_cameras;
DESCRIBE detection_logs;

-- ================= SUCCESS MESSAGE =================
SELECT 'Additional features tables created successfully!' AS message;
