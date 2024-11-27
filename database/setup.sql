-- Creates the database.
CREATE DATABASE IF NOT EXISTS GenericCompany;
USE GenericCompany;

-- SCHEMA: Enumerated Types --
  -- Employment --
CREATE TABLE IF NOT EXISTS Departments (
  Name CHAR(36) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT DepartmentsCK_ValidName
    CHECK ( NAME REGEXP '^[-&/ a-zA-Z]+$' )
);
CREATE TABLE IF NOT EXISTS EmploymentTypes (
  Name CHAR(16) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT EmploymentTypesCK_ValidName
    CHECK ( NAME REGEXP '^[- a-zA-Z]+$' )
);
CREATE TABLE IF NOT EXISTS Positions (
  Name CHAR(36) NOT NULL,
  MinimumSalary INT NOT NULL,
  MaximumSalary INT NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT PositionsCK_ValidName
    CHECK ( NAME REGEXP '^[-&/ a-zA-Z0-9]+$' ),
  CONSTRAINT PositionsCK_ValidSalaryRange
    CHECK ( -- Enforce minimum wage...?
      MinimumSalary > 0 AND
      MinimumSalary <= MaximumSalary
  )
);
CREATE TABLE IF NOT EXISTS Benefits (
  Name CHAR(24) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT BenefitsCK_ValidName
    CHECK ( NAME REGEXP '^[-&/ a-zA-Z]+$' )
);
  -- Project Management --
CREATE TABLE IF NOT EXISTS ProjectStatus (
  Name CHAR(16) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT ProjectStatusCK_ValidName
    CHECK ( Name REGEXP '^[- a-zA-Z]+$' )
);
CREATE TABLE IF NOT EXISTS ProjectRoles (
  Name CHAR(36) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT ProjectRolesCK_ValidName
    CHECK ( Name REGEXP '^[-&/ a-zA-Z0-9]+$' )
);
  -- Demographics --
CREATE TABLE IF NOT EXISTS Genders (
  Name CHAR(8) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT GendersCK_ValidName
    CHECK ( Name REGEXP '^[- a-zA-Z]+$' )
);
CREATE TABLE IF NOT EXISTS States (
  Name CHAR(2) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT StatesCK_ValidName
    CHECK ( Name REGEXP '^[A-Z]{2}$' )
);
CREATE TABLE IF NOT EXISTS Degrees (
  Name CHAR(16) NOT NULL,
  PRIMARY KEY (Name)
);

-- SCHEMA: Employee Records --
CREATE TABLE IF NOT EXISTS Employees (
  ID INT NOT NULL AUTO_INCREMENT,
  FirstName CHAR(16) NOT NULL,
  LastName CHAR(16) NOT NULL,
  Gender CHAR(8) NOT NULL,
  BirthDate DATE NOT NULL,
  SocialSecurity CHAR(11) NOT NULL,
  PhoneNumber CHAR(10) NOT NULL,
  StreetAddress VARCHAR(255) NOT NULL,
  City VARCHAR(64) NOT NULL,
  State CHAR(2) NOT NULL,
  ZIPCode CHAR(10) NOT NULL,
  HighestDegree CHAR(8) NULL,
  ExternalYearsWorked SMALLINT NOT NULL,
  PRIMARY KEY (ID),
  CONSTRAINT EmployeesFK_Gender
    FOREIGN KEY (Gender)
    REFERENCES Genders (Name)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT EmployeesUK_SocialSecurity
    UNIQUE (SocialSecurity),
  CONSTRAINT EmployeesCK_SocialSecurityFormat
    CHECK ( SocialSecurity REGEXP '^[0-9]{3}-[0-9]{2}-[0-9]{4}$' ),
  CONSTRAINT EmployeesCK_ValidPhoneNumber
    CHECK ( PhoneNumber REGEXP '^[0-9]{10}$' ),
  CONSTRAINT EmployeesCK_ValidAddress
    CHECK (
      StreetAddress REGEXP '^[-&/(),.'' a-zA-Z0-9]+$' AND
      City REGEXP '^[-,.'' a-zA-Z0-9]+$' AND
      ZIPCode REGEXP '^[0-9]{5}(-[0-9]{4})?$'
  ),
  CONSTRAINT EmployeesFK_State
    FOREIGN KEY (State)
    REFERENCES States (Name)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT EmployeesFK_HighestDegree
    FOREIGN KEY (HighestDegree)
    REFERENCES Degrees (Name)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT EmployeesCK_ValidYears
    CHECK ( ExternalYearsWorked >= 0 )
);

-- TODO:
---- Log warning when Salary is out-of-range.
---- Log warning when DateRange overlaps with each other.
---- Trigger update to History with each insert/update.
---- Require specifying EndDate with each delete.
CREATE TABLE IF NOT EXISTS EmployeePositions (
  ID INT NOT NULL,
  StartDate DATE NOT NULL,
  Position CHAR(36) NOT NULL,
  EmploymentType CHAR(16) NOT NULL,
  Salary INT NOT NULL,
  IsExternalHire TINYINT NOT NULL,
  HealthCoverageStartDate DATE NULL,
  HealthCoverageEndDate DATE NULL,
  PRIMARY KEY (ID),
  CONSTRAINT EmployeePositionsFK_ID
    FOREIGN KEY (ID)
    REFERENCES Employees (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT EmployeePositionsFK_Position
    FOREIGN KEY (Position)
    REFERENCES Positions (Name)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT EmployeePositionsFK_EmploymentType
    FOREIGN KEY (EmploymentType)
    REFERENCES EmploymentTypes (Name),
    -- ON DELETE RESTRICT --
    -- ON UPDATE RESTRICT --
  CONSTRAINT EmployeePositionsCK_ValidSalary
    CHECK ( Salary >= 0 ),
  CONSTRAINT EmployeePositionsCK_RequiredHealthCoverage
    CHECK (
      EmploymentType != 'Full-Time' OR
      HealthCoverageStartDate IS NOT NULL
  ),
  CONSTRAINT EmployeePositionsCK_ValidHealthCoverageDateRange
    CHECK (
      HealthCoverageStartDate IS NULL OR
      HealthCoverageEndDate IS NULL OR
      HealthCoverageEndDate >= HealthCoverageStartDate
  )
);
CREATE TABLE IF NOT EXISTS EmployeePositionsHistory (
  ID INT NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NULL,
  Position CHAR(36) NOT NULL,
  EmploymentType CHAR(16) NOT NULL,
  Salary INT NOT NULL,
  IsExternalHire TINYINT NOT NULL,
  HealthCoverageStartDate DATE NULL,
  HealthCoverageEndDate DATE NULL,
  PRIMARY KEY (ID, StartDate),
  CONSTRAINT EmployeePositionsHistoryFK_ID
    FOREIGN KEY (ID)
    REFERENCES Employees (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT EmployeePositionsHistoryCK_ValidDateRange
    CHECK (
      EndDate IS NULL OR
      EndDate >= StartDate
  )
);

-- TODO:
---- Log warning when DateRange overlaps with each other.
---- Trigger update to History with each insert/update.
---- Require specifying EndDate with each delete.
CREATE TABLE IF NOT EXISTS EmployeeDepartments (
  ID INT NOT NULL,
  Department CHAR(36) NOT NULL,
  StartDate DATE NOT NULL,
  PRIMARY KEY (ID, Department),
  CONSTRAINT EmployeeDepartmentsFK_ID
    FOREIGN KEY (ID)
    REFERENCES Employees (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeDepartmentsFK_Department
    FOREIGN KEY (Department)
    REFERENCES Departments (Name)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS EmployeeDepartmentsHistory (
  ID INT NOT NULL,
  Department CHAR(36) NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NULL,
  PRIMARY KEY (ID, Department, StartDate),
  CONSTRAINT EmployeeDepartmentsHistoryFK_ID
    FOREIGN KEY (ID)
    REFERENCES Employees (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeDepartmentsHistoryCK_ValidDateRange
    CHECK (
      EndDate IS NULL OR
      EndDate >= StartDate
  )
);

CREATE TABLE IF NOT EXISTS EmployeeBenefits (
  ID INT NOT NULL,
  Benefit CHAR(24) NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NULL,
  PRIMARY KEY (ID, Benefit),
  CONSTRAINT EmployeeBenefitsFK_ID
    FOREIGN KEY (ID)
    REFERENCES Employees (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeBenefitsFK_Benefit
    FOREIGN KEY (Benefit)
    REFERENCES Benefits (Name)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeBenefitsCK_ValidDateRange
    CHECK (
      EndDate IS NULL OR
      EndDate >= StartDate
  )
);

-- SCHEMA: Project Records --
CREATE TABLE IF NOT EXISTS Projects (
  ID INT NOT NULL AUTO_INCREMENT,
  Name VARCHAR(255) NOT NULL,
  Department CHAR(36) NOT NULL,
  Status CHAR(16) NOT NULL,
  Leader INT NOT NULL,
  PRIMARY KEY (ID),
  CONSTRAINT ProjectsFK_Department
    FOREIGN KEY (Department)
    REFERENCES Departments (Name)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT ProjectsFK_Status
    FOREIGN KEY (Status)
    REFERENCES ProjectStatus (Name)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT ProjectsFK_Leader
    FOREIGN KEY (Leader)
    REFERENCES Employees (ID)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE
);

-- TODO:
---- Log warning when DateRange overlaps with each other.
---- Trigger update to History with each insert/update.
---- Require specifying EndDate with each delete.
CREATE TABLE IF NOT EXISTS EmployeeRoles (
  EmployeeID INT NOT NULL,
  ProjectID INT NOT NULL,
  StartDate DATE NOT NULL,
  Role CHAR(36) NOT NULL,
  PRIMARY KEY (EmployeeID, ProjectID),
  CONSTRAINT EmployeeRolesFK_EmployeeID
    FOREIGN KEY (EmployeeID)
    REFERENCES Employees (ID)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeRolesFK_ProjectID
    FOREIGN KEY (ProjectID)
    REFERENCES Projects (ID)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeRolesFK_Role
    FOREIGN KEY (Role)
    REFERENCES ProjectRoles (Name)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS EmployeeRolesHistory (
  EmployeeID INT NOT NULL,
  ProjectID INT NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NULL,
  Role CHAR(36) NOT NULL,
  PRIMARY KEY (EmployeeID, ProjectID, StartDate),
  CONSTRAINT EmployeeRolesHistoryFK_EmployeeID
    FOREIGN KEY (EmployeeID)
    REFERENCES Employees (ID)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeRolesHistoryFK_ProjectID
    FOREIGN KEY (ProjectID)
    REFERENCES Projects (ID)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE
);

-- Creates new users for this database only.
CREATE USER IF NOT EXISTS 'GenericAdministrator'@'localhost';
CREATE USER IF NOT EXISTS 'GenericApplication'@'localhost';
-- Grants necessary privileges.
GRANT ALL PRIVILEGES ON GenericCompany.*
  TO 'GenericAdministrator'@'localhost';
GRANT SELECT ON GenericCompany.*
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.Positions
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.Benefits
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.ProjectStatus
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.ProjectRoles
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE
  ON GenericCompany.Employees
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.EmployeePositions
  TO 'GenericApplication'@'localhost';
GRANT UPDATE(StartDate, EndDate)
  ON GenericCompany.EmployeePositionsHistory
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.EmployeeDepartments
  TO 'GenericApplication'@'localhost';
GRANT UPDATE(StartDate, EndDate)
  ON GenericCompany.EmployeeDepartmentsHistory
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.EmployeeBenefits
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE
  ON GenericCompany.Projects
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.EmployeeRoles
  TO 'GenericApplication'@'localhost';
GRANT INSERT, UPDATE, DELETE
  ON GenericCompany.EmployeeRolesHistory
  TO 'GenericApplication'@'localhost';
FLUSH PRIVILEGES;
