import random
import MySQLdb
from flask import current_app, g
from faker import Faker

def open_db():
    if 'db' not in g:
        g.db = MySQLdb.connect(
            current_app.config['MYSQL_HOST'],
            current_app.config['MYSQL_USER'],
            current_app.config['MYSQL_PASSWORD'],
            current_app.config['MYSQL_DB']
        )

    return g.db

def close_db(e=None):
    db = g.pop('db', e)

    if db is not None:
        db.close()

def modify_db(query: str, args=None):
    db = open_db()
    cursor = db.cursor()

    try:
        cursor.execute(query, args)
        db.commit()
    except MySQLdb.Error:
        db.rollback()
        raise
    finally:
        cursor.close()
        close_db()

def search_db(query: str, cursor_type, multi=True, args=None):
    db = open_db()
    cursor = db.cursor(cursor_type)

    try:
        cursor.execute(query, args)
        if not multi:
            return cursor.fetchone()
        else:
            return cursor.fetchall()
    finally:
        cursor.close()
        close_db()

def init_db(app):
    app.teardown_appcontext(close_db)
    generate_and_insert_fake_data(app, 1000)

def generate_and_insert_fake_data(app, records, batch_size=100):
    faker = Faker()
    conn = MySQLdb.connect(
        app.config['MYSQL_HOST'],
        app.config['MYSQL_USER'],
        app.config['MYSQL_PASSWORD'],
        app.config['MYSQL_DB']
    )
    cursor = conn.cursor()

    if cursor.execute("SELECT ID FROM Staff") >= records:
        print("Using existing data")
        cursor.close()
        conn.close()
        return

    # Fetch valid departments, positions, and benefits from the database
    cursor.execute("SELECT Name FROM Departments")
    valid_departments = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT Name FROM Positions")
    valid_positions = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT Name FROM Benefits")
    valid_benefits = [row[0] for row in cursor.fetchall()]

    staff_data = []
    positions_data = []
    departments_data = []
    benefits_data = []

    for _ in range(records):
        # Generate staff data
        first_name = faker.first_name()
        last_name = faker.last_name()
        gender = random.choice(['Male', 'Female'])
        birth_date = faker.date_of_birth(minimum_age=18, maximum_age=65)
        social_security = faker.ssn().format('###-##-####')
        phone_number = faker.msisdn()[:10]
        street_address = faker.street_address()
        city = faker.city()
        state = faker.state_abbr(False, False)
        zip_code = faker.zipcode()
        highest_degree = random.choice([None, 'Diploma', 'Associate', 'Bachelor', 'Master', 'Doctoral'])
        external_years_worked = random.randint(0, 40)
        staff_data.append((first_name, last_name, gender, birth_date, social_security, phone_number,
                           street_address, city, state, zip_code, highest_degree, external_years_worked))

        # Once inserted, retrieve the auto-generated ID
        if len(staff_data) >= batch_size:
            cursor.executemany("""
                INSERT INTO Staff (
                    FirstName, LastName, Gender, BirthDate, SocialSecurity,
                    PhoneNumber, StreetAddress, City, State, ZIPCode,
                    HighestDegree, ExternalYearsWorked
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, tuple(staff_data))

            # Retrieve the IDs of the inserted staff
            id = cursor.lastrowid
            for i in range(len(staff_data)):
                staff_id = id + i

                # Generate a single position
                start_date = faker.date_between(start_date='-10y', end_date='today')
                salary = random.randint(40000, 120000)
                positions_data.append((staff_id, start_date, None, random.choice(valid_positions),
                                       random.choice(['Full-Time', 'Part-Time']), salary, random.choice([0, 1]), start_date, None))

                # Generate multiple departments
                num_departments = random.randint(1, 3)
                unique_departments = list(valid_departments)
                for _ in range(num_departments):
                    department = random.choice(unique_departments)
                    unique_departments.remove(department)
                    departments_data.append((staff_id, department, start_date, None))

                # Generate benefits
                num_benefits = random.randint(1, 4)
                unique_benefits = list(valid_benefits)
                for _ in range(num_benefits):
                    benefit = random.choice(unique_benefits)
                    unique_benefits.remove(benefit)
                    benefit_start_date = faker.date_between(start_date=start_date, end_date='today')
                    benefits_data.append((staff_id, benefit, benefit_start_date, None))

            # Clear staff_data after insertion
            staff_data = []

    # Insert remaining positions, departments, and benefits
    if positions_data:
        cursor.executemany("""
            INSERT INTO PositionsHistory (
                ID, StartDate, EndDate, Position, EmploymentType, Salary,
                IsExternalHire, HealthCoverageStartDate, HealthCoverageEndDate
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, positions_data)

    if departments_data:
        cursor.executemany("""
            INSERT INTO DepartmentsHistory (
                ID, Department, StartDate, EndDate
            ) VALUES (%s, %s, %s, %s)
        """, departments_data)

    if benefits_data:
        cursor.executemany("""
            INSERT INTO StaffBenefits (
                ID, Benefit, StartDate, EndDate
            ) VALUES (%s, %s, %s, %s)
        """, benefits_data)

    # Commit the transactions and close the connection
    conn.commit()
    cursor.close()
    conn.close()
