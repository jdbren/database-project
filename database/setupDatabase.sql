-- Creates a new database.
CREATE DATABASE IF NOT EXISTS GenericCompany;
-- Creates a new user for this database only.
CREATE USER IF NOT EXISTS 'Administrator'@'localhost';
-- Grants all privileges. (Restrict this...)
GRANT ALL PRIVILEGES ON GenericCompany.*
  TO 'Administrator'@'localhost';
FLUSH PRIVILEGES;
