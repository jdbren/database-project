DELIMITER $$

-- EmployeePositions --
DROP TRIGGER IF EXISTS AfterPositionInsert $$
CREATE TRIGGER AfterPositionInsert
AFTER INSERT ON EmployeePositions
FOR EACH ROW
  BEGIN
    INSERT INTO EmployeePositionsHistory
    VALUES ( NEW.ID, NEW.StartDate, NULL,
      NEW.Position, NEW.EmploymentType,
      NEW.Salary, NEW.IsExternalHire,
      NEW.HealthInsurance,
      NEW.HealthStartDate,
      NEW.HealthEndDate
    );
  END $$

DROP TRIGGER IF EXISTS BeforePositionUpdate $$
CREATE TRIGGER BeforePositionUpdate
BEFORE UPDATE ON EmployeePositions
FOR EACH ROW
  BEGIN
    DECLARE hasConflicts INT;

    SELECT COUNT(*)
    INTO hasConflicts
    FROM EmployeePositionsHistory
    WHERE ID = NEW.ID AND
      StartDate != NEW.StartDate AND
      NEW.StartDate BETWEEN StartDate AND EndDate;
    -- Technically, EndDate can be NULL. However, CONSTRAINT checks
    -- guarantees that only one NULL EndDate exists at any time;
    -- in short, NULL EndDate passes this check but fails uniqueness.

    IF hasConflicts > 0 THEN
      SIGNAL SQLSTATE '45000' -- User-defined error.
      SET MESSAGE_TEXT = 'StartDate conflicts with previous records.';
    END IF;
  END $$
DROP TRIGGER IF EXISTS AfterPositionUpdate $$
CREATE TRIGGER AfterPositionUpdate
AFTER UPDATE ON EmployeePositions
FOR EACH ROW
  BEGIN
    UPDATE EmployeePositionsHistory
    SET ID = NEW.ID, StartDate = NEW.StartDate,
      Position = NEW.Position, EmploymentType = NEW.EmploymentType,
      Salary = NEW.Salary, IsExternalHire = NEW.IsExternalHire,
      HealthInsurance = NEW.HealthInsurance,
      HealthStartDate = NEW.HealthStartDate,
      HealthEndDate = NEW.HealthEndDate
    WHERE ID = OLD.ID AND StartDate = OLD.StartDate;
  END $$

DROP TRIGGER IF EXISTS AfterPositionDelete $$
CREATE TRIGGER AfterPositionDelete
AFTER DELETE ON EmployeePositions
FOR EACH ROW
  BEGIN
    IF @disablePositionTrigger IS NULL THEN
      DELETE FROM EmployeePositionsHistory
      WHERE ID = OLD.ID AND EndDate IS NULL;
    END IF;
  END $$
DROP PROCEDURE IF EXISTS RetireFromPosition $$
CREATE PROCEDURE RetireFromPosition(
  IN Employee INT, IN PositionEndDate DATE
)
BEGIN
  START TRANSACTION;
  SET @disablePositionTrigger = 1;

  UPDATE EmployeePositionsHistory
  SET EndDate = PositionEndDate
  WHERE ID = Employee AND EndDate IS NULL;
  DELETE FROM EmployeePositions
  WHERE ID = Employee;

  SET @disablePositionTrigger = NULL;
  COMMIT;
END $$

-- EmployeeDepartments --
DROP TRIGGER IF EXISTS AfterDepartmentInsert $$
CREATE TRIGGER AfterDepartmentInsert
AFTER INSERT ON EmployeeDepartments
FOR EACH ROW
  BEGIN
    INSERT INTO EmployeeDepartmentsHistory
    VALUES ( NEW.ID, NEW.Department, NEW.StartDate, NULL );
  END $$

DROP TRIGGER IF EXISTS BeforeDepartmentUpdate $$
CREATE TRIGGER BeforeDepartmentUpdate
BEFORE UPDATE ON EmployeeDepartments
FOR EACH ROW
  BEGIN
    DECLARE hasConflicts INT;

    SELECT COUNT(*)
    INTO hasConflicts
    FROM EmployeeDepartmentsHistory
    WHERE ID = NEW.ID AND
      Department = NEW.Department AND
      StartDate != NEW.StartDate AND
      NEW.StartDate BETWEEN StartDate AND EndDate;
    -- Technically, EndDate can be NULL. However, CONSTRAINT checks
    -- guarantees that only one NULL EndDate exists at any time;
    -- in short, NULL EndDate passes this check but fails uniqueness.

    IF hasConflicts > 0 THEN
      SIGNAL SQLSTATE '45000' -- User-defined error.
      SET MESSAGE_TEXT = 'StartDate conflicts with previous records.';
    END IF;
  END $$
DROP TRIGGER IF EXISTS AfterDepartmentUpdate $$
CREATE TRIGGER AfterDepartmentUpdate
AFTER UPDATE ON EmployeeDepartments
FOR EACH ROW
  BEGIN
    UPDATE EmployeeDepartmentsHistory
    SET ID = NEW.ID,
      Department = NEW.Department,
      StartDate = NEW.StartDate
    WHERE ID = OLD.ID AND
      Department = OLD.Department AND
      StartDate = OLD.StartDate;
  END $$

DROP TRIGGER IF EXISTS AfterDepartmentDelete $$
CREATE TRIGGER AfterDepartmentDelete
AFTER DELETE ON EmployeeDepartments
FOR EACH ROW
  BEGIN
    IF @disableDepartmentTrigger IS NULL THEN
      DELETE FROM EmployeeDepartmentsHistory
      WHERE ID = OLD.ID AND
        Department = OLD.Department AND
        EndDate IS NULL;
    END IF;
  END $$
DROP PROCEDURE IF EXISTS LeaveDepartment $$
CREATE PROCEDURE LeaveDepartment(
  IN Employee INT, IN Team CHAR(36),
  IN DepartmentEndDate DATE
)
BEGIN
  START TRANSACTION;
  SET @disableDepartmentTrigger = 1;

  UPDATE EmployeeDepartmentsHistory
  SET EndDate = DepartmentEndDate
  WHERE ID = Employee AND
    Department = Team AND
    EndDate IS NULL;
  DELETE FROM EmployeeDepartments
  WHERE ID = Employee AND
    Department = Team;

  SET @disableDepartmentTrigger = NULL;
  COMMIT;
END $$

-- Delete Employee From Active Tables --
DROP PROCEDURE IF EXISTS ArchiveEmployee $$
CREATE PROCEDURE ArchiveEmployee(
  IN Employee INT, IN ArchiveDate DATE
)
BEGIN
  START TRANSACTION;
  SET @disablePositionTrigger = 1;
  SET @disableDepartmentTrigger = 1;
  SET @disableEmployeeRoleTrigger = 1;

  UPDATE EmployeePositionsHistory
    SET EndDate = ArchiveDate
    WHERE ID = Employee AND EndDate IS NULL;
  DELETE FROM EmployeePositions
    WHERE ID = Employee;

  UPDATE EmployeeDepartmentsHistory
    SET EndDate = ArchiveDate
    WHERE ID = Employee AND EndDate IS NULL;
  DELETE FROM EmployeeDepartments
    WHERE ID = Employee;

  UPDATE EmployeeRolesHistory
    SET EndDate = ArchiveDate
    WHERE EmployeeID = Employee AND EndDate IS NULL;
  DELETE FROM EmployeeRoles
    WHERE EmployeeID = Employee;

  DELETE FROM EmployeeBenefits
    WHERE ID = Employee;

  SET @disablePositionTrigger = NULL;
  SET @disableDepartmentTrigger = NULL;
  SET @disableEmployeeRoleTrigger = NULL;
  COMMIT;
END $$

-- Project --
DROP PROCEDURE IF EXISTS CreateProject $$
CREATE PROCEDURE CreateProject(
  IN Title VARCHAR(255), IN Team CHAR(36),
  IN TeamLeader INT, IN ProjectStartDate DATE
)
BEGIN
  DECLARE newProjectID INT;

  START TRANSACTION;

  INSERT INTO Projects(Name, Department, Status, Leader)
  VALUES ( Title, Team, 'Not Started', TeamLeader );
  SET newProjectID = LAST_INSERT_ID();
  INSERT INTO EmployeeRolesHistory
  VALUES ( TeamLeader, newProjectID,
    ProjectStartDate, NULL, 'Leader'
  );
  COMMIT;
END $$

DROP TRIGGER IF EXISTS BeforeProjectUpdate $$
CREATE TRIGGER BeforeProjectUpdate
BEFORE UPDATE ON Projects
FOR EACH ROW
  BEGIN
    DECLARE isClosed INT;

    IF @disableProjectTrigger IS NULL THEN

      SELECT COUNT(*)
      INTO isClosed
      FROM Projects
      WHERE ID = NEW.ID AND
        Status = 'Closed';

      IF isClosed = 0 AND NEW.Status = 'Closed' THEN
        SIGNAL SQLSTATE '45000' -- User-defined error.
        SET MESSAGE_TEXT = 'Closing project requires CloseProject().';
      ELSEIF isClosed > 1 AND NEW.Status != 'Closed' THEN
        SIGNAL SQLSTATE '45000' -- User-defined error.
        SET MESSAGE_TEXT = 'Re-opening project requires ReviveProject().';
      ELSEIF OLD.Leader != NEW.Leader THEN
        SIGNAL SQLSTATE '45000' -- User-defined error.
        SET MESSAGE_TEXT = 'Leader update requires ChangeProjectLeader().';
      END IF;
    END IF;
  END $$
DROP PROCEDURE IF EXISTS CloseProject $$
CREATE PROCEDURE CloseProject(
  IN Project INT, IN CloseDate DATE
)
BEGIN
  DECLARE isEmpty INT DEFAULT NULL;
  DECLARE employee INT;
  DECLARE roleCursor CURSOR FOR
    SELECT EmployeeID FROM EmployeeRoles
    WHERE ProjectID = Project;
  DECLARE CONTINUE HANDLER FOR
    NOT FOUND SET isEmpty = 1;

  START TRANSACTION;
  SET @disableProjectTrigger = 1;

  OPEN roleCursor;
  retireAll: LOOP
    FETCH roleCursor INTO employee;
    IF isEmpty THEN LEAVE retireAll; END IF;
    CALL RetireFromRole(employee, CloseDate);
  END LOOP;
  CLOSE roleCursor;

  UPDATE Projects
  SET Status = 'Closed'
  WHERE ID = Project;

  SET @disableProjectTrigger = NULL;
  COMMIT;
END $$
DROP PROCEDURE IF EXISTS ReviveProject $$
CREATE PROCEDURE ReviveProject(
  IN Project INT, IN ReviveDate DATE,
  IN TeamLeader INT
)
BEGIN
  START TRANSACTION;
  SET @disableProjectTrigger = 1;

  UPDATE Projects
  SET Status = 'In Progress'
  WHERE ID = Project;
  IF TeamLeader IS NOT NULL THEN
    UPDATE Projects
    SET Leader= TeamLeader
    WHERE ID = Project;
  END IF;
  INSERT INTO EmployeeRolesHistory
  VALUES ( TeamLeader, Project,
    ReviveDate, NULL, 'Leader'
  );

  SET @disableProjectTrigger = NULL;
  COMMIT;
END $$
DROP PROCEDURE IF EXISTS ChangeProjectLeader $$
CREATE PROCEDURE ChangeProjectLeader(
  IN Project INT, IN NewTeamLeader INT,
  IN ChangeDate DATE
)
BEGIN
  DECLARE isSameLeader INT;

  START TRANSACTION;
  SET @disableProjectTrigger = 1;

  SELECT COUNT(*)
  INTO isSameLeader
  FROM Projects
  WHERE ID = Project AND
    Leader = NewTeamLeader;

  IF isSameLeader = 0 THEN
    UPDATE EmployeeRolesHistory
    SET EndDate = ChangeDate
    WHERE ProjectID = Project AND
      EndDate IS NULL AND
      Role = 'Leader';
    INSERT INTO EmployeeRolesHistory
    VALUES ( NewTeamLeader, Project,
      ChangeDate, NULL, 'Leader'
    );
    UPDATE Projects
    SET Leader = NewTeamLeader
    WHERE ProjectID = Project;
  END IF;

  SET @disableProjectTrigger = NULL;
  COMMIT;
END $$

-- EmployeeRoles --
DROP TRIGGER IF EXISTS AfterEmployeeRoleInsert $$
CREATE TRIGGER AfterEmployeeRoleInsert
AFTER INSERT ON EmployeeRoles
FOR EACH ROW
  BEGIN
    INSERT INTO EmployeeRolesHistory
    VALUES ( NEW.EmployeeID, NEW.ProjectID,
      NEW.StartDate, NULL, NEW.Role
    );
  END $$

DROP TRIGGER IF EXISTS BeforeEmployeeRoleUpdate $$
CREATE TRIGGER BeforeEmployeeRoleUpdate
BEFORE UPDATE ON EmployeeRoles
FOR EACH ROW
  BEGIN
    DECLARE hasConflicts INT;

    SELECT COUNT(*)
    INTO hasConflicts
    FROM EmployeeRolesHistory
    WHERE EmployeeID = NEW.EmployeeID AND
      ProjectID = NEW.ProjectID AND
      StartDate != NEW.StartDate AND
      NEW.StartDate BETWEEN StartDate AND EndDate;
    -- Technically, EndDate can be NULL. However, CONSTRAINT checks
    -- guarantees that only one NULL EndDate exists at any time;
    -- in short, NULL EndDate passes this check but fails uniqueness.

    IF hasConflicts > 0 THEN
      SIGNAL SQLSTATE '45000' -- User-defined error.
      SET MESSAGE_TEXT = 'StartDate conflicts with previous records.';
    END IF;
  END $$
DROP TRIGGER IF EXISTS AfterEmployeeRoleUpdate $$
CREATE TRIGGER AfterEmployeeRoleUpdate
AFTER UPDATE ON EmployeeRoles
FOR EACH ROW
  BEGIN
    UPDATE EmployeeRolesHistory
    SET EmployeeID = NEW.EmployeeID,
      ProjectID = NEW.ProjectID,
      StartDate = NEW.StartDate,
      Role = NEW.Role
    WHERE EmployeeID = OLD.EmployeeID AND
      ProjectID = OLD.ProjectID AND
      StartDate = OLD.StartDate;
  END $$

DROP TRIGGER IF EXISTS AfterEmployeeRoleDelete $$
CREATE TRIGGER AfterEmployeeRoleDelete
AFTER DELETE ON EmployeeRoles
FOR EACH ROW
  BEGIN
    IF @disableEmployeeRoleTrigger IS NULL THEN
      DELETE FROM EmployeeRolesHistory
      WHERE EmployeeID = OLD.EmployeeID AND
        ProjectID = OLD.ProjectID AND
        EndDate IS NULL;
    END IF;
  END $$
DROP PROCEDURE IF EXISTS RetireFromRole $$
CREATE PROCEDURE RetireFromRole(
  IN Employee INT, IN Project INT,
  IN EmployeeRoleEndDate DATE
)
BEGIN
  START TRANSACTION;
  SET @disableEmployeeRoleTrigger = 1;

  UPDATE EmployeeRolesHistory
  SET EndDate = EmployeeRoleEndDate
  WHERE EmployeeID = Employee AND
    ProjectID = Project AND
    EndDate IS NULL;
  DELETE FROM EmployeeRoles
  WHERE EmployeeID = Employee AND
    ProjectID = Project;

  SET @disableEmployeeRoleTrigger = NULL;
  COMMIT;
END $$

DELIMITER ;
