from http import HTTPStatus
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from app.db import (
    execute_and_fetchall, execute_and_fetchone, execute_and_commit, get_db, close_db
)
from MySQLdb import cursors

bp = Blueprint('employee', __name__, url_prefix='/employee')

@bp.route('/')
def index():
    return render_template('employee/index.html')

## TODO: Add more than one department and health insurance
@bp.route('/insert', methods=['GET', 'POST'])
def insert():
    benefitsList = execute_and_fetchall('SELECT Name FROM Benefits', cursors.DictCursor)

    if request.method == 'POST':
        try:
            # Retrieve form data
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
            position = request.form['position']
            employment_type = request.form['employment_type']
            selected_departments = request.form.getlist('departments')
            salary = request.form['salary']
            health_insurance = None
            external_hire = request.form['external_hire']
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
                    IsExternalHire
                ) VALUES (%s, CURDATE(), %s, %s, %s, %s)
            ''', (id, position, employment_type, salary, external_hire))

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

            return redirect('/employee', HTTPStatus.CREATED)

        except Exception as e:
            print(e)
            return "Error", 500

    positionsList = execute_and_fetchall('SELECT Name FROM Positions', cursors.DictCursor)
    departmentsList = execute_and_fetchall('SELECT Name FROM Departments', cursors.DictCursor)
    return render_template('employee/insert.html',
        positions=positionsList,
        departments=departmentsList,
        benefits=benefitsList
    )



@bp.get('/search')
def search():
    employees = execute_and_fetchall('SELECT * FROM Staff', cursors.Cursor)
    return render_template('employee/search.html', employees=employees)

@bp.route('/<int:id>', methods=['GET', 'POST'])
def view(id):
    return ""

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        return redirect('/employee', HTTPStatus.OK)
    emp = execute_and_fetchone('SELECT * FROM Staff WHERE ID = %s', cursors.DictCursor, (id,))

    return render_template('employee/edit.html', emp=emp)
