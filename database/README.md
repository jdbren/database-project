# Quick Start
The following commands must be run from the repository's root directory.
To initialize the database: `mysql -u root -p < ./database/initialize.sql`
To insert default data: `python ./database/insertDefault.py`

## Scripts
- `initialize.sql`: Creates 'GenericCompany' with 'GenericAdministrator' and 'GenericApplciation' users, granting all privileges to 'GenericAdministrator' and limited privileges to 'GenericApplication'.
    - `schema.sql`: Defines database schemas.
    - `sproc.sql`: Defines stored procedures and triggers.
- `insertDefault.py`: Populates database with default enumerations from `default`.
- `insertSimulate.py`: Populates database with random simulated data.

## Credits
- Name data from [Mockaroo](https://mockaroo.com).
- Address data from [Real, Random Address Date](https://github.com/EthanRBrown/rrad).

# Reference
*Consult `schema.sql` for available tables and attributes.*

## Stored Procedures
- `CreateProject(Title, Department, TeamLead, StartDate)`: Creates a new project, with a corresponding record for the project leader.
- `CloseProject(ProjectID, CloseDate)`: Closes the project, removing all active employees from the project. See `RetireFromRole()`.
- `ReviveProject(ProjectID, OpenDate, TeamLead)`: Revives an existing project, with a corresponding record for the project Leader. See `CreateProject()`.
- `ChangeProjectLeader(ProjectID, TeamLead, ChangeDate)`: Replaces the current project leader with the new project leader. See `RetireFromRole()`.

"Linked" operations are operations on active tables that trigger the corresponding operations on historical tables. INSERT, UPDATE, DELETE fall under this category. The following stored procedures are unlinked:

- `RetireFromPosition(EmployeeID, EndDate)`: Deletes record of employee's position from active table but not from historical table. This is the default method for updating and removing.
- `LeaveDepartment(EmployeeID, Department, EndDate)`: Deletes record of employee's involvement with the department from active table but not from historical table. This is the default method for updating and removing.
- `RetireFromRole(EmployeeID, ProjectID, EndDate)`: Deletes record of employee's role from active table but not from historical table. This is the default method for updating and removing.

## Triggers
All AFTER triggers sync historical and active tables, whereas BEFORE triggers validate that new StartDate cannot conflict with existing records. Each of `EmployeePositions`, `EmployeeDepartments`, and `EmployeeRoles` have both triggers. `Projects` have a special BEFORE trigger, which enforces correct usage of the appropriate update procedures.
