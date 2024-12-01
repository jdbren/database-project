-- SCHEMA: Enumerated Types --
  -- Employment --
CREATE TABLE IF NOT EXISTS Departments (
  Name CHAR(36) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT DepartmentsCK_ValidName
    CHECK ( Name REGEXP '^[-&/ a-zA-Z]+$' )
);
CREATE TABLE IF NOT EXISTS EmploymentTypes (
  Name CHAR(16) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT EmploymentTypesCK_ValidName
    CHECK ( Name REGEXP '^[-&/ a-zA-Z]+$' )
);
CREATE TABLE IF NOT EXISTS Positions (
  Name CHAR(36) NOT NULL,
  MinimumSalary INT NOT NULL,
  MaximumSalary INT NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT PositionsCK_ValidName
    CHECK ( Name REGEXP '^[-&/ a-zA-Z0-9]+$' ),
  CONSTRAINT PositionsCK_ValidSalaryRange
    CHECK ( MinimumSalary > 0 AND
      MinimumSalary <= MaximumSalary
  )
);
CREATE TABLE IF NOT EXISTS HealthInsurance (
  Name CHAR(36) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT HealthInsuranceCK_ValidName
    CHECK ( Name REGEXP '^[-&/ a-zA-Z0-9]+$' )
);
CREATE TABLE IF NOT EXISTS Benefits (
  Name CHAR(24) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT BenefitsCK_ValidName
    CHECK ( Name REGEXP '^[-&/ a-zA-Z0-9]+$' )
    -- Excludes all types of Health Insurances.
);
  -- Project Management --
CREATE TABLE IF NOT EXISTS ProjectStatus (
  Name CHAR(16) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT ProjectStatusCK_ValidName
    CHECK ( Name REGEXP '^[-&/ a-zA-Z0-9]+$' )
);
CREATE TABLE IF NOT EXISTS ProjectRoles (
  Name CHAR(36) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT ProjectRolesCK_ValidName
    CHECK ( Name != 'Leader' AND
      Name REGEXP '^[-&/ a-zA-Z0-9]+$'
  ) -- 'Leader' is reserved!
);
  -- Demographics --
CREATE TABLE IF NOT EXISTS Genders (
  Name CHAR(8) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT GendersCK_ValidName
    CHECK ( Name REGEXP '^[-&/ a-zA-Z]+$' )
);
CREATE TABLE IF NOT EXISTS States (
  Name CHAR(2) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT StatesCK_ValidName
    CHECK ( Name REGEXP '^[A-Z]{2}$' )
);
CREATE TABLE IF NOT EXISTS Degrees (
  Name CHAR(32) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT DegreesCK_ValidName
    CHECK ( Name REGEXP '^[.'' a-zA-Z]+$' )
);

-- SCHEMA: Employee Records --
CREATE TABLE IF NOT EXISTS Employees (
  ID INT NOT NULL AUTO_INCREMENT,
  FirstName CHAR(16) NOT NULL,
  LastName CHAR(16) NOT NULL,
  Gender CHAR(8) NOT NULL,
  BirthDate DATE NOT NULL,
  SocialSecurity CHAR(11) NOT NULL,
  PhoneNumber CHAR(12) NOT NULL,
  StreetAddress VARCHAR(255) NOT NULL,
  City VARCHAR(64) NOT NULL,
  State CHAR(2) NOT NULL,
  ZIPCode CHAR(10) NOT NULL,
  HighestDegree CHAR(32) NULL,
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
    CHECK ( PhoneNumber REGEXP '^[0-9]{3} [0-9]{3}-[0-9]{4}$' ),
  CONSTRAINT EmployeesCK_ValidAddress
    CHECK ( -- Or have one field for the entire address.
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

CREATE TABLE IF NOT EXISTS EmployeePositions (
  ID INT NOT NULL,
  StartDate DATE NOT NULL,
  Position CHAR(36) NOT NULL,
  EmploymentType CHAR(16) NOT NULL,
  Salary INT NOT NULL,
  IsExternalHire TINYINT NOT NULL,
  HealthInsurance CHAR(36) NULL,
  HealthStartDate DATE NULL,
  HealthEndDate DATE NULL,
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
    REFERENCES EmploymentTypes (Name)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT EmployeePositionsFK_HealthInsurance
    FOREIGN KEY (HealthInsurance)
    REFERENCES HealthInsurance (Name)
    -- ON DELETE RESTRICT --
    ON UPDATE CASCADE,
  CONSTRAINT EmployeePositionsCK_ValidSalary
    CHECK ( Salary >= 0 ),
  CONSTRAINT EmployeePositionsCK_ValidHealthDateRange
    CHECK ( HealthStartDate IS NULL OR HealthEndDate IS NULL OR
      HealthEndDate >= HealthStartDate
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
  HealthInsurance CHAR(36) NULL,
  HealthStartDate DATE NULL,
  HealthEndDate DATE NULL,
  PRIMARY KEY (ID, StartDate),
  CONSTRAINT EmployeePositionsHistoryFK_ID
    FOREIGN KEY (ID)
    REFERENCES Employees (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT EmployeePositionsHistoryCK_ValidDateRange
    CHECK ( EndDate IS NULL OR EndDate >= StartDate ),
  CONSTRAINT EmployeePositionsHistoryCK_ValidSalary
    CHECK ( Salary >= 0 ),
  CONSTRAINT EmployeePositionsHistoryCK_ValidHealthDateRange
    CHECK ( HealthStartDate IS NULL OR HealthEndDate IS NULL OR
      HealthEndDate >= HealthStartDate
  )
);

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
    CHECK ( EndDate IS NULL OR EndDate >= StartDate )
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
    CHECK ( EndDate IS NULL OR EndDate >= StartDate )
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
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS EmployeeRoles (
  EmployeeID INT NOT NULL,
  ProjectID INT NOT NULL,
  StartDate DATE NOT NULL,
  Role CHAR(36) NOT NULL,
  PRIMARY KEY (EmployeeID, ProjectID),
  CONSTRAINT EmployeeRolesFK_EmployeeID
    FOREIGN KEY (EmployeeID)
    REFERENCES Employees (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeRolesFK_ProjectID
    FOREIGN KEY (ProjectID)
    REFERENCES Projects (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeRolesFK_Role
    FOREIGN KEY (Role)
    REFERENCES ProjectRoles (Name)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS EmployeeRolesHistory (
  EmployeeID INT NOT NULL,
  ProjectID INT NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NULL,
  Role CHAR(36) NOT NULL,
  PRIMARY KEY (EmployeeID, ProjectID, StartDate, Role),
  CONSTRAINT EmployeeRolesHistoryFK_EmployeeID
    FOREIGN KEY (EmployeeID)
    REFERENCES Employees (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeRolesHistoryFK_ProjectID
    FOREIGN KEY (ProjectID)
    REFERENCES Projects (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT EmployeeRolesHistoryCK_ValidDateRange
    CHECK ( EndDate IS NULL OR EndDate >= StartDate )
);
