from datetime import datetime
from http import HTTPStatus
from MySQLdb import cursors
from flask import ( Blueprint, render_template,
    flash, redirect, request, session, url_for
)
from app.db import (
    search_db, modify_db, open_db, close_db
)

bp = Blueprint('employee', __name__, url_prefix='/employee')

@bp.route('/')
def index():
    return render_template('employee/index.html')

## TODO: Add more than one department and health insurance
@bp.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        try:
            # Employees data
            ssn = request.form['ssn']
            fname = request.form['first_name']
            lname = request.form['last_name']
            gender = request.form['gender']
            dob = request.form['dob']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            postcode = request.form['zip']
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

            db = open_db()
            cursor = db.cursor()

            # Insert data into the database
            cursor.execute('''
                INSERT INTO Employees (
                    SocialSecurity, FirstName, LastName, Gender, BirthDate,
                    StreetAddress, City, State, ZIPCode, PhoneNumber, HighestDegree,
                    ExternalYearsWorked
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (ssn, fname, lname, gender, dob, address, city, state, postcode,
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
                    INSERT INTO EmployeeBenefits (
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

    benefitsList = search_db('SELECT Name FROM Benefits', cursors.DictCursor)
    positionsList = search_db('SELECT Name FROM Positions', cursors.DictCursor)
    departmentsList = search_db('SELECT Name FROM Departments', cursors.DictCursor)
    return render_template('employee/form.html',
        positions=positionsList,
        departments=departmentsList,
        benefits=benefitsList
    )



@bp.get('/search')
def search():
    employees = search_db('SELECT * FROM Employees', cursors.Cursor)
    return render_template('employee/search.html', employees=employees)

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
            # Employees data
            ssn = request.form['ssn']
            fname = request.form['first_name']
            lname = request.form['last_name']
            gender = request.form['gender']
            dob = request.form['dob']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            postcode = request.form['zip']
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

            db = open_db()
            cursor = db.cursor()

            # Update data in the database
            cursor.execute('''
                UPDATE Employees
                SET SocialSecurity = %s, FirstName = %s, LastName = %s, Gender = %s,
                    BirthDate = %s, StreetAddress = %s, City = %s, State = %s,
                    ZIPCode = %s, PhoneNumber = %s, HighestDegree = %s,
                    ExternalYearsWorked = %s
                WHERE ID = %s
            ''', (ssn, fname, lname, gender, dob, address, city, state, postcode,
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
                        UPDATE EmployeeBenefits
                        SET EndDate = CURDATE()
                        WHERE ID = %s AND Benefit = %s AND EndDate IS NULL
                    ''', (id, benefit))

            # Add new benefits
            for benefit in selected_benefits:
                if benefit not in currentBenefits:
                    cursor.execute('''
                        INSERT INTO EmployeeBenefits (
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


    emp = search_db('SELECT * FROM Employees WHERE ID = %s', cursors.DictCursor, False, (id,))
    benefitsList = search_db('SELECT Name FROM Benefits', cursors.DictCursor)
    positionsList = search_db('SELECT Name FROM Positions', cursors.DictCursor)
    departmentsList = search_db('SELECT Name FROM Departments', cursors.DictCursor)

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
    currentDepartments = search_db('''
        SELECT Department FROM DepartmentsHistory WHERE ID = %s AND EndDate IS NULL
    ''', cursors.Cursor, (id,))
    currentDepartments = [department[0] for department in currentDepartments]
    return currentDepartments

def get_employee_benefits(id):
    currentBenefits = search_db('''
        SELECT Benefit FROM EmployeeBenefits WHERE ID = %s AND EndDate IS NULL
    ''', cursors.Cursor, (id,))
    currentBenefits = [benefit[0] for benefit in currentBenefits]
    return currentBenefits

def get_employee_position(id):
    return search_db('''
        SELECT Salary, Position FROM PositionsHistory WHERE ID = %s AND EndDate IS NULL
    ''', cursors.DictCursor, (id,), False)
