-- Create match_logs table if it doesn't exist
CREATE TABLE IF NOT EXISTS match_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id VARCHAR(50) NOT NULL,
    camera_id INT,
    confidence DECIMAL(5,2),
    match_image VARCHAR(255),
    cctv_image VARCHAR(255),
    status ENUM('MATCH FOUND', 'NO MATCH', 'PENDING') DEFAULT 'MATCH FOUND',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_person_id (person_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert some test match logs for demonstration
INSERT INTO match_logs (person_id, camera_id, confidence, status) VALUES
('person_101', 1, 85.50, 'MATCH FOUND'),
('person_102', 2, 78.30, 'MATCH FOUND'),
('person_103', 1, 92.10, 'MATCH FOUND');

-- Create detection_alerts table if it doesn't exist (should already exist)
-- This is just in case
CREATE TABLE IF NOT EXISTS detection_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT,
    police_user_id INT,
    message TEXT,
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_is_read (is_read),
    INDEX idx_match_id (match_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert some test alerts
INSERT INTO detection_alerts (match_id, police_user_id, message, is_read) VALUES
(1, 1, 'AI match found for person_101 with 85.50% confidence', 0),
(2, 1, 'AI match found for person_102 with 78.30% confidence', 0),
(3, 1, 'AI match found for person_103 with 92.10% confidence', 0);

-- Also add to detection_logs for analytics
CREATE TABLE IF NOT EXISTS detection_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id VARCHAR(50),
    camera_id INT,
    confidence DECIMAL(5,2),
    status ENUM('MATCH FOUND', 'NO MATCH', 'PENDING') DEFAULT 'PENDING',
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert test detection logs
INSERT INTO detection_logs (person_id, camera_id, confidence, status) VALUES
('person_101', 1, 85.50, 'MATCH FOUND'),
('person_102', 2, 78.30, 'MATCH FOUND'),
('person_103', 1, 92.10, 'MATCH FOUND');
