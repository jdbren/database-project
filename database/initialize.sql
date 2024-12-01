-- Creates the database.
CREATE DATABASE IF NOT EXISTS GenericCompany;
USE GenericCompany;
-- Creates the tables.
SOURCE ./database/schema.sql;
SOURCE ./database/sproc.sql;

-- Creates new users for this database only.
CREATE USER IF NOT EXISTS 'GenericAdministrator'@'localhost';
CREATE USER IF NOT EXISTS 'GenericApplication'@'localhost';
-- Grants necessary privileges.
GRANT ALL PRIVILEGES ON GenericCompany.*
  TO 'GenericAdministrator'@'localhost';

GRANT SELECT ON GenericCompany.*
  TO 'GenericApplication'@'localhost';

-- Departments: Raise a ticket!
-- This should go through an approval process
--  before submitting a request to the DBA.
--  Request by Executives.

-- EmploymentTypes: Raise a ticket!
-- This should go through an approval process
--  before submitting a request to the DBA.
--  Request by Human Resources.

GRANT INSERT, UPDATE
  ON GenericCompany.Positions
  TO 'GenericApplication'@'localhost';
-- We should have separate privileges, but
--  this is outside of the scope of the assignment.
--  I.e. Create a user dedicated to Human Resources.
-- Note: Do NOT expose or modify ID.

-- Benefits: Raise a ticket!
-- This should go through an approval process
--  before submitting a request to the DBA.
--  Request by Compensation & Benefits.

-- ProjectStatus: Raise a ticket!
--  Request by Project Management.

GRANT INSERT, UPDATE
  ON GenericCompany.ProjectRoles
  TO 'GenericApplication'@'localhost';
-- We should have separate privileges, but
--  this is outside of the scope of the assignment.
--  I.e. Create a user dedicated to Project Management.

-- Genders: Raise a ticket!
--  Request by Data Analysts.

-- States: Raise a ticket!
--  Request by Data Analysts.

-- Degrees: Raise a ticket!
--  Request by Data Analysts.

GRANT INSERT, UPDATE
  ON GenericCompany.Employees
  TO 'GenericApplication'@'localhost';
-- We should have separate privileges, but
--  this is outside of the scope of the assignment.
--  Deletion should require approval from Compliance.
--  I.e. Create a user dedicated to Human Resources.

GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.EmployeePositions
  TO 'GenericApplication'@'localhost';
GRANT EXECUTE
  ON PROCEDURE GenericCompany.RetireFromPosition
  TO 'GenericApplication'@'localhost';

-- EmployeePositionsHistory: Raise a ticket!
-- It is malpractice to modify historic data.
--  Requests should be carefully reviewed
--  before submitting a request to the DBA.
--  Request by Human Resources.

GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.EmployeeDepartments
  TO 'GenericApplication'@'localhost';
GRANT EXECUTE
  ON PROCEDURE GenericCompany.LeaveDepartment
  TO 'GenericApplication'@'localhost';

-- EmployeeDepartmentsHistory: Raise a ticket!
-- It is malpractice to modify historic data.
--  Requests should be carefully reviewed
--  before submitting a request to the DBA.
--  Request by Human Resources.

GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.EmployeeBenefits
  TO 'GenericApplication'@'localhost';
-- We should have separate privileges, but
--  this is outside of the scope of the assignment.
--  I.e. Create a user dedicated to Human Resources.

GRANT UPDATE
  ON GenericCompany.Projects
  TO 'GenericApplication'@'localhost';
GRANT EXECUTE
  ON PROCEDURE GenericCompany.CreateProject
  TO 'GenericApplication'@'localhost';
GRANT EXECUTE
  ON PROCEDURE GenericCompany.CloseProject
  TO 'GenericApplication'@'localhost';
GRANT EXECUTE
  ON PROCEDURE GenericCompany.ReviveProject
  TO 'GenericApplication'@'localhost';
GRANT EXECUTE
  ON PROCEDURE GenericCompany.ChangeProjectLeader
  TO 'GenericApplication'@'localhost';

GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.EmployeeRoles
  TO 'GenericApplication'@'localhost';
GRANT EXECUTE
  ON PROCEDURE GenericCompany.RetireFromRole
  TO 'GenericApplication'@'localhost';

-- ProjectRolesHistory: Raise a ticket!
-- It is malpractice to modify historic data.
--  Requests should be carefully reviewed
--  before submitting a request to the DBA.
--  Request by Project Management.

FLUSH PRIVILEGES;
