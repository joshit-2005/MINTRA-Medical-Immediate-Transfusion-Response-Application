CREATE DATABASE blood_system;
USE blood_system;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(200),
    role ENUM('donor','receiver') DEFAULT 'donor'
);

CREATE TABLE donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    blood_group VARCHAR(5),
    city VARCHAR(100),
    phone VARCHAR(15),
    last_donation DATE,
    available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    receiver_name VARCHAR(100),
    blood_group VARCHAR(5),
    city VARCHAR(100),
    units INT,
    hospital VARCHAR(200),
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);