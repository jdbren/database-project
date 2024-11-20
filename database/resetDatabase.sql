-- Drops the database.
DROP DATABASE IF EXISTS GenericCompany;
-- Drops the user for this database only.
DROP USER IF EXISTS 'Administrator'@'localhost';

-- Re-creates the database.
-- This file should be run in 'root' directory.
SOURCE ./database/setupDatabase.sql
