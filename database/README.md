# Quick Start

The following command must be run from the repository's root directory.

To start the database, run: `mysql -u root -p < ./database/initialize.sql`

To insert default data, run: `python ./database/insertDefault.py`.

## Scripts
- `initialize.sql`: Creates `GenericCompany` with `GenericAdministrator` and `GenericApplication` users, granting all privileges to `GenericAdministrator` and limited privileges to `GenericApplication`. Sources `schema.sql` and `sproc.sql`.
- `insertDefault.py`: Populates tables with sample data from `default`.
- `insertSimulate.py`: Populates tables with random simulated data.
