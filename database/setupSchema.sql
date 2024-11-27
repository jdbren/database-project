-- Company Enumerated Types --
CREATE TABLE IF NOT EXISTS Departments (
  Name CHAR(36) NOT NULL,
  CONSTRAINT DepartmentsPK
    PRIMARY KEY (Name),
  CONSTRAINT DepartmentsCK_ValidName CHECK (
    Name REGEXP '^[a-zA-Z/ ]+$'
  )
);
CREATE TABLE IF NOT EXISTS EmploymentTypes (
  Name CHAR(16) NOT NULL,
  CONSTRAINT EmploymentTypesPK
    PRIMARY KEY (Name),
  CONSTRAINT EmploymentTypesCK_ValidName CHECK (
    Name REGEXP '^[-a-zA-Z]+$'
  )
);
CREATE TABLE IF NOT EXISTS Positions (
  Name CHAR(36) NOT NULL,
  MinimumSalary INT NOT NULL,
  MaximumSalary INT NOT NULL,
  CONSTRAINT PositionsPK
    PRIMARY KEY (Name),
  CONSTRAINT PositionsCK_ValidName CHECK (
    Name REGEXP '^[a-zA-Z/ ]+$'
  ),
  CONSTRAINT PositionsCK_ValidRange CHECK (
    -- Maybe enforce minimum wage...
    MinimumSalary > 0 AND
    MinimumSalary < MaximumSalary
  )
);
CREATE TABLE IF NOT EXISTS Benefits (
  Name CHAR(24) NOT NULL,
  CONSTRAINT BenefitsPK
    PRIMARY KEY (Name),
  CONSTRAINT BenefitsCK_ValidName CHECK (
    Name REGEXP '^[a-zA-Z/ ]+$'
  )
);
CREATE TABLE IF NOT EXISTS ProjectRoles (
  Name CHAR(36) NOT NULL,
  CONSTRAINT ProjectRolesPK
    PRIMARY KEY (Name),
  CONSTRAINT ProjectRolesCK_ValidName CHECK (
    Name REGEXP '^[a-zA-Z/ ]+$'
  )
);

-- Project Records --
CREATE TABLE IF NOT EXISTS Projects (
  Name VARCHAR(255) NOT NULL,
  Department CHAR(36) NOT NULL,
  Status ENUM(
    'New', 'In-Progress',
    'On-Hold', 'Complete'
  ) NOT NULL,
  CONSTRAINT ProjectsPK
    PRIMARY KEY (Name),
  CONSTRAINT ProjectsFK_Department
    FOREIGN KEY (Department)
    REFERENCES Departments (Name)
    -- ON DELETE RESTRICT...
    ON UPDATE CASCADE
);

-- Demographic Enumerated Types --
CREATE TABLE IF NOT EXISTS States (
  Name CHAR(2) NOT NULL,
  CONSTRAINT StatesPK
    PRIMARY KEY (Name),
  CONSTRAINT StatesCK_ValidName CHECK (
    Name REGEXP '^[A-Z]{2}$'
  )
);
CREATE TABLE IF NOT EXISTS Degrees (
  Name CHAR(12) NOT NULL,
  CONSTRAINT DegreesPK
    PRIMARY KEY (Name)
);

-- Employee Records --
CREATE TABLE IF NOT EXISTS Staff (
  ID INT NOT NULL AUTO_INCREMENT,
  FirstName CHAR(16) NOT NULL,
  LastName CHAR(16) NOT NULL,
  Gender ENUM(
    'Male', 'Female', 'Other',
    'Prefer Not to Say'
  ) NOT NULL,
  BirthDate DATE NOT NULL,
  SocialSecurity CHAR(11) NOT NULL,
  PhoneNumber CHAR(10) NOT NULL,
  StreetAddress VARCHAR(255) NOT NULL,
  City VARCHAR(64) NOT NULL,
  State CHAR(2) NOT NULL,
  ZIPCode CHAR(10) NOT NULL,
  HighestDegree CHAR(16) NULL,
  ExternalYearsWorked SMALLINT NOT NULL,
  CONSTRAINT StaffPK
    PRIMARY KEY (ID),
  CONSTRAINT StaffUK_SocialSecurity
    UNIQUE (SocialSecurity),
  CONSTRAINT StaffCK_SocialSecurityFormat CHECK (
    SocialSecurity REGEXP '^[0-9]{3}-[0-9]{2}-[0-9]{4}$'
  ),
  CONSTRAINT StaffCK_ValidPhoneNumber CHECK (
    PhoneNumber REGEXP '^[0-9]{10}$'
  ),
  CONSTRAINT StaffFK_State
    FOREIGN KEY (State)
    REFERENCES States (Name)
    -- ON DELETE RESTRICT...
    ON UPDATE CASCADE,
  CONSTRAINT StaffCK_ValidZIP CHECK (
    ZIPCode REGEXP '^[0-9]{5}(-[0-9]{4})?$'
  ),
  CONSTRAINT StaffFK_HighestDegree
    FOREIGN KEY (HighestDegree)
    REFERENCES Degrees (Name)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT StaffCK_ValidYears CHECK (
    ExternalYearsWorked > 0
  )
);

CREATE TABLE IF NOT EXISTS StaffBenefits (
  ID INT NOT NULL,
  Benefit CHAR(24) NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NULL,
  CONSTRAINT StaffBenefitsPK
    PRIMARY KEY (ID, Benefit),
  CONSTRAINT StaffBenefitsFK_ID
    FOREIGN KEY (ID)
    REFERENCES Staff (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT StaffBenefitsFK_Benefit
    FOREIGN KEY (Benefit)
    REFERENCES Benefits (Name)
    -- ON DELETE RESTRICT...
    ON UPDATE CASCADE,
  CONSTRAINT StaffBenefitsCK_ValidRange CHECK (
    EndDate IS NULL OR
    EndDate > StartDate
  )
);

CREATE TABLE IF NOT EXISTS PositionsHistory (
  ID INT NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NULL,
  Position CHAR(36) NOT NULL,
  EmploymentType CHAR(16) NOT NULL,
  Salary INT NOT NULL,
  IsExternalHire TINYINT NOT NULL,
  HealthCoverageStartDate DATE NULL,
  HealthCoverageEndDate DATE NULL,
  CONSTRAINT PositionsHistoryPK
    PRIMARY KEY (ID, StartDate),
  CONSTRAINT PositionsHistoryFK_ID
    FOREIGN KEY (ID)
    REFERENCES Staff (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT PositionsHistoryCK_ValidRange CHECK (
    EndDate IS NULL OR
    EndDate > StartDate
  ),
  CONSTRAINT PositionsHistoryFK_Position
    FOREIGN KEY (Position)
    REFERENCES Positions (Name)
    -- ON DELETE RESTRICT...
    ON UPDATE CASCADE,
  CONSTRAINT PositionsHistoryFK_EmploymentType
    FOREIGN KEY (EmploymentType)
    REFERENCES EmploymentTypes (Name),
    -- ON DELETE RESTRICT...
    -- ON UPDATE RESTRICT...
  CONSTRAINT PositionsHistoryCK_ValidSalary CHECK (
    -- Not possible to enforce range...
    Salary > 0
  ),
  CONSTRAINT PositionsHistoryCK_ValidRangeHealth CHECK (
    HealthCoverageStartDate IS NULL OR
    HealthCoverageEndDate IS NULL OR
    HealthCoverageEndDate > HealthCoverageStartDate
  ),
  CONSTRAINT PositionsHistoryCK_RequiredHealthCoverage CHECK (
    EmploymentType != 'Full-Time' OR
    HealthCoverageStartDate IS NOT NULL
  )
);

CREATE TABLE IF NOT EXISTS DepartmentsHistory (
  ID INT NOT NULL,
  Department CHAR(36) NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NULL,
  CONSTRAINT DepartmentsHistoryPK
    PRIMARY KEY (ID, Department, StartDate),
  CONSTRAINT DepartmentsHistoryFK_ID
    FOREIGN KEY (ID)
    REFERENCES Staff (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT DepartmentsHistoryFK_Department
    FOREIGN KEY (Department)
    REFERENCES Departments (Name)
    -- ON DELETE RESTRICT...
    ON UPDATE CASCADE,
  CONSTRAINT DepartmentsHistoryCK_ValidRange CHECK (
    EndDate IS NULL OR
    EndDate > StartDate
  )
);

CREATE TABLE IF NOT EXISTS ProjectRolesHistory (
  ID INT NOT NULL,
  Project CHAR(255) NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NULL,
  Role CHAR(36) NOT NULL,
  CONSTRAINT ProjectRolesHistoryPK
    PRIMARY KEY (ID, Project, StartDate),
  CONSTRAINT ProjectRolesHistoryFK_ID
    FOREIGN KEY (ID)
    REFERENCES Staff (ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT ProjectRolesHistoryFK_Project
    FOREIGN KEY (Project)
    REFERENCES Projects (Name)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT ProjectRolesHistoryCK_ValidRange CHECK (
    EndDate IS NULL OR
    EndDate > StartDate
  ),
  CONSTRAINT ProjectRolesHistoryFK_Role
    FOREIGN KEY (Role)
    REFERENCES ProjectRoles (Name)
    -- ON DELETE RESTRICT
    ON UPDATE CASCADE
);
