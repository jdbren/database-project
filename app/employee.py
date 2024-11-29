from http import HTTPStatus
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from app.db import (
    execute_and_fetchall, execute_and_fetchone, execute_and_commit, get_db, close_db
)
from MySQLdb import cursors
from datetime import datetime

bp = Blueprint('employee', __name__, url_prefix='/employee')

@bp.route('/')
def index():
    return render_template('employee/index.html')

## TODO: Add more than one department and health insurance
@bp.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        try:
            # Staff data
            ssn = request.form['ssn']
            fname = request.form['first_name']
            lname = request.form['last_name']
            gender = request.form['gender']
            dob = request.form['dob']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            zip = request.form['zip']
            phone = request.form['phone']
            degree = None
            if request.form['degree']:
                degree = request.form['degree']
            experience = request.form['experience']
            # PositionsHistory data
            position = request.form['position']
            employment_type = request.form['employment_type']
            salary = request.form['salary']
            health_insurance = request.form['health_insurance']
            health_insurance_start_date = None
            if health_insurance == 'company':
                health_insurance_start_date = datetime.date(datetime.now())
            external_hire = request.form['external_hire']
            # DepartmentsHistory data
            selected_departments = request.form.getlist('departments')
            # BenefitsHistory data
            selected_benefits = request.form.getlist('benefits')

            db = get_db()
            cursor = db.cursor()

            # Insert data into the database
            cursor.execute('''
                INSERT INTO Staff (
                    SocialSecurity, FirstName, LastName, Gender, BirthDate,
                    StreetAddress, City, State, ZIPCode, PhoneNumber, HighestDegree,
                    ExternalYearsWorked
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (ssn, fname, lname, gender, dob, address, city, state, zip,
                phone, degree, experience)
            )

            id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO PositionsHistory (
                    ID, StartDate, Position, EmploymentType, Salary,
                    IsExternalHire, HealthCoverageStartDate
                ) VALUES (%s, CURDATE(), %s, %s, %s, %s, %s)
            ''', (id, position, employment_type, salary, external_hire,
                health_insurance_start_date)
            )

            for department in selected_departments:
                cursor.execute('''
                    INSERT INTO DepartmentsHistory (
                        ID, Department, StartDate
                    ) VALUES (%s, %s, CURDATE())
                ''', (id, department))

            for benefit in selected_benefits:
                cursor.execute('''
                    INSERT INTO StaffBenefits (
                        ID, Benefit, StartDate
                    ) VALUES (%s, %s, CURDATE())
                ''', (id, benefit))

            cursor.close()

            # Commit the transaction
            db.commit()
            close_db()

            flash('Employee added successfully')
            return redirect('/employee', HTTPStatus.CREATED)

        except Exception as e:
            print(e)
            flash('An error occurred while adding the employee')
            return "Error", HTTPStatus.INTERNAL_SERVER_ERROR

    benefitsList = execute_and_fetchall('SELECT Name FROM Benefits', cursors.DictCursor)
    positionsList = execute_and_fetchall('SELECT Name FROM Positions', cursors.DictCursor)
    departmentsList = execute_and_fetchall('SELECT Name FROM Departments', cursors.DictCursor)
    return render_template('employee/form.html',
        positions=positionsList,
        departments=departmentsList,
        benefits=benefitsList
    )



@bp.get('/search')
def search():
    fname = request.args.get('first_name')
    lname = request.args.get('last_name')
    ssn = request.args.get('ssn')
    phone = request.args.get('phone')
    gender = request.args.get('gender')
    degree = request.args.get('degree')
    position = request.args.get('position')
    salary_min = request.args.get('salary_min')
    salary_max = request.args.get('salary_max')
    try:
        # Construct SQL query
        query = """
            SELECT
                s.ID,
                s.FirstName,
                s.LastName,
                s.Gender,
                s.BirthDate,
                s.SocialSecurity,
                s.PhoneNumber,
                s.StreetAddress,
                s.City,
                s.State,
                s.ZIPCode,
                s.HighestDegree,
                s.ExternalYearsWorked,
                GROUP_CONCAT(DISTINCT dh.Department ORDER BY dh.StartDate SEPARATOR ', ') AS Departments,
                ph.Position,
                ph.Salary
            FROM
                Staff AS s
            LEFT JOIN
                DepartmentsHistory AS dh
                ON s.ID = dh.ID AND dh.EndDate IS NULL
            LEFT JOIN
                PositionsHistory AS ph
                ON s.ID = ph.ID AND ph.EndDate IS NULL
        """

        # Build WHERE conditions dynamically
        conditions = []
        params = {}

        if fname:
            conditions.append("(s.FirstName LIKE %(fname)s")
            params['fname'] = f"%{fname}%"
        if lname:
            conditions.append("s.LastName LIKE %(lname)s")
            params['lname'] = f"%{lname}%"
        if ssn:
            conditions.append("s.SocialSecurity = %(ssn)s")
            params['ssn'] = ssn
        if phone:
            conditions.append("s.PhoneNumber = %(phone)s")
            params['phone'] = phone
        if gender:
            conditions.append("s.Gender = %(gender)s")
            params['gender'] = gender
        if degree:
            conditions.append("s.HighestDegree = %(degree)s")
            params['degree'] = degree
        if position:
            conditions.append("ph.Position = %(position)s")
            params['position'] = position
        if salary_min:
            conditions.append("ph.Salary >= %(salary_min)s")
            params['salary_min'] = salary_min
        if salary_max:
            conditions.append("ph.Salary <= %(salary_max)s")
            params['salary_max'] = salary_max

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += """
            GROUP BY
                s.ID, s.FirstName, s.LastName, s.Gender, s.BirthDate, s.SocialSecurity,
                s.PhoneNumber, s.StreetAddress, s.City, s.State, s.ZIPCode,
                s.HighestDegree, s.ExternalYearsWorked, ph.Position, ph.Salary
        """
        print(query)
        results = execute_and_fetchall(query, cursors.Cursor, params)

        positionsList = execute_and_fetchall('SELECT Name FROM Positions', cursors.DictCursor)
        return render_template('employee/search.html',
            employees=results,
            positions=positionsList)
    except Exception as e:
        print(e)
        flash('An error occurred while fetching the employees')
        return "Error", HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<int:id>', methods=['GET', 'POST'])
def view(id):
    return ""

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    currentPosition = get_employee_position(id)
    currentDepartments = get_employee_departments(id)
    currentBenefits = get_employee_benefits(id)
    if request.method == 'POST':
        try:
            # Staff data
            ssn = request.form['ssn']
            fname = request.form['first_name']
            lname = request.form['last_name']
            gender = request.form['gender']
            dob = request.form['dob']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            zip = request.form['zip']
            phone = request.form['phone']
            degree = None
            if request.form['degree']:
                degree = request.form['degree']
            experience = request.form['experience']
            # PositionsHistory data
            position = request.form['position']
            employment_type = request.form['employment_type']
            salary = request.form['salary']
            health_insurance = request.form['health_insurance']
            health_insurance_start_date = None
            if health_insurance == 'company':
                health_insurance_start_date = datetime.date(datetime.now())
            external_hire = request.form['external_hire']
            # DepartmentsHistory data
            selected_departments = request.form.getlist('departments')
            # BenefitsHistory data
            selected_benefits = request.form.getlist('benefits')

            db = get_db()
            cursor = db.cursor()

            # Update data in the database
            cursor.execute('''
                UPDATE Staff
                SET SocialSecurity = %s, FirstName = %s, LastName = %s, Gender = %s,
                    BirthDate = %s, StreetAddress = %s, City = %s, State = %s,
                    ZIPCode = %s, PhoneNumber = %s, HighestDegree = %s,
                    ExternalYearsWorked = %s
                WHERE ID = %s
            ''', (ssn, fname, lname, gender, dob, address, city, state, zip,
                phone, degree, experience, id)
            )

            if (currentPosition['Position'] != position
            or currentPosition['Salary'] != salary
            or currentPosition['EmploymentType'] != employment_type):
                # Update the old record, maybe make this trigger
                cursor.execute('''
                    UPDATE PositionsHistory
                    SET EndDate = CURDATE()
                    WHERE ID = %s AND EndDate IS NULL
                ''', (id,))
                # Insert updated information
                cursor.execute('''
                    INSERT INTO PositionsHistory (
                        ID, StartDate, Position, EmploymentType, Salary,
                        IsExternalHire, HealthCoverageStartDate
                    ) VALUES (%s, CURDATE(), %s, %s, %s, 0, %s)
                ''', (id, position, employment_type, salary,
                    health_insurance_start_date))

            # Update departments no longer associated with the employee
            for department in currentDepartments:
                if department not in selected_departments:
                    cursor.execute('''
                        UPDATE DepartmentsHistory
                        SET EndDate = CURDATE()
                        WHERE ID = %s AND Department = %s AND EndDate IS NULL
                    ''', (id, department))

            # Add new departments
            for department in selected_departments:
                if department not in currentDepartments:
                    cursor.execute('''
                        INSERT INTO DepartmentsHistory (
                            ID, Department, StartDate
                        ) VALUES (%s, %s, CURDATE())
                    ''', (id, department))

            # Update benefits no longer associated with the employee
            for benefit in currentBenefits:
                if benefit not in selected_benefits:
                    cursor.execute('''
                        UPDATE StaffBenefits
                        SET EndDate = CURDATE()
                        WHERE ID = %s AND Benefit = %s AND EndDate IS NULL
                    ''', (id, benefit))

            # Add new benefits
            for benefit in selected_benefits:
                if benefit not in currentBenefits:
                    cursor.execute('''
                        INSERT INTO StaffBenefits (
                            ID, Benefit, StartDate
                        ) VALUES (%s, %s, CURDATE())
                    ''', (id, benefit))

            cursor.close()
            db.commit()
            close_db()

            return redirect('/employee', HTTPStatus.ACCEPTED)
        except Exception as e:
            print(e)
            flash('An error occurred while updating the employee')
            return "Error", HTTPStatus.INTERNAL_SERVER_ERROR


    emp = execute_and_fetchone('SELECT * FROM Staff WHERE ID = %s', cursors.DictCursor, (id,))
    benefitsList = execute_and_fetchall('SELECT Name FROM Benefits', cursors.DictCursor)
    positionsList = execute_and_fetchall('SELECT Name FROM Positions', cursors.DictCursor)
    departmentsList = execute_and_fetchall('SELECT Name FROM Departments', cursors.DictCursor)

    emp['Departments'] = currentDepartments
    emp['Benefits'] = currentBenefits
    emp['Salary'] = currentPosition['Salary']
    emp['Position'] = currentPosition['Position']
    return render_template('employee/form.html',
        emp=emp,
        positions=positionsList,
        departments=departmentsList,
        benefits=benefitsList
    )

@bp.post('<int:id>/delete')
def delete(id):
    return ""


def get_employee_departments(id):
    currentDepartments = execute_and_fetchall('''
        SELECT Department FROM DepartmentsHistory WHERE ID = %s AND EndDate IS NULL
    ''', cursors.Cursor, (id,))
    currentDepartments = [department[0] for department in currentDepartments]
    return currentDepartments

def get_employee_benefits(id):
    currentBenefits = execute_and_fetchall('''
        SELECT Benefit FROM StaffBenefits WHERE ID = %s AND EndDate IS NULL
    ''', cursors.Cursor, (id,))
    currentBenefits = [benefit[0] for benefit in currentBenefits]
    return currentBenefits

def get_employee_position(id):
    return execute_and_fetchone('''
        SELECT Salary, Position FROM PositionsHistory WHERE ID = %s AND EndDate IS NULL
    ''', cursors.DictCursor, (id,))
