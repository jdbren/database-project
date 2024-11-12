# Quick Start

To setup the database, start `mysql` as root and run
```mysql
SOURCE ./database/setupDatabase.sql
```

This scripts creates the `GenericCompany` database with an `Administrator` user. You can continue as root or, better yet, run as `Administrator`. To create tables and insert sample data, run
```mysql
USE GenericCompany;
SOURCE ./database/setupSchema.sql
SOURCE ./database/insertData.sql
```

## Scripts
- `setupDatabase.sql`: Creates `GenericCompany` with `Administrator` user, granting all privileges to `Administrator`.
- `resetDatabase.sql`: Drops the database and the user before sourcing `setupDatabase.sql`.
- `setupSchema.sql`: Creates all tables.
- `insertData.sql`: Populates tables with sample data.
