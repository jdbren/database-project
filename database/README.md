# Quick Start

To start the database, run (assuming password-protected root):
```bash
mysql -u root -p < ./database/setup.sql
```

To insert sample data, run: `python ./database/insertBase.py` from the repository's root directory.

## Scripts
- `insertBase.py`: Populates tables with sample data from `data`.
- `insertSimulate.py`: Populates tables with random simulated data.
- `setup.sql`: Creates `GenericCompany` with `GenericAdministrator` and `GenericApplication` users, granting all privileges to `GenericAdministrator` and limited privileges to `GenericApplication`.
- `wipe.sql`: Drops the database and users.
