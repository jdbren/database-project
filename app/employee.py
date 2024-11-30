from datetime import datetime
from MySQLdb import cursors
from http import HTTPStatus
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
            # EmployeePositions data
            position = request.form['position']
            employment_type = request.form['employment_type']
            salary = request.form['salary']
            health_insurance = request.form['health_insurance']
            health_insurance_start_date = None
            if health_insurance == 'company':
                health_insurance_start_date = datetime.date(datetime.now())
            external_hire = request.form['external_hire']
            # EmployeeDepartments data
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
                phone, degree, experience))

            id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO EmployeePositions (
                    ID, StartDate, Position, EmploymentType, Salary,
                    IsExternalHire, HealthInsurance, HealthStartDate
                ) VALUES (%s, CURDATE(), %s, %s, %s, %s, %s, %s)
            ''', (id, position, employment_type, salary, external_hire,
                health_insurance, health_insurance_start_date)
            )

            for department in selected_departments:
                cursor.execute('''
                    INSERT INTO EmployeeDepartments (
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

    genders_list = search_db('SELECT Name FROM Genders', cursors.DictCursor)
    degrees_list = search_db('SELECT Name FROM Degrees', cursors.DictCursor)
    benefits_list = search_db('SELECT Name FROM Benefits', cursors.DictCursor)
    positions_list = search_db('SELECT Name FROM Positions', cursors.DictCursor)
    departments_list = search_db('SELECT Name FROM Departments', cursors.DictCursor)
    return render_template('employee/form.html',
        departments=departments_list,
        positions=positions_list,
        benefits=benefits_list,
        degrees=degrees_list,
        genders=genders_list
    )



@bp.get('/search')
def search():
    fname = request.args.get('first_name')
    lname = request.args.get('last_name')
    ssn = request.args.get('ssn')
    id = request.args.get('employee_number')
    phone = request.args.get('phone')
    gender = request.args.get('gender')
    degree = request.args.get('degree')
    experience = request.args.get('experience')
    position = request.args.get('position')
    salary_min = request.args.get('salary_min')
    salary_max = request.args.get('salary_max')
    address = request.args.get('address')
    city = request.args.get('city')
    state = request.args.get('state')
    zip_code = request.args.get('zip')
    employment_type = request.args.get('employment_type')
    departments = request.args.getlist('departments')
    try:
        # Construct SQL query
        query = """
            SELECT
                s.ID,
                s.SocialSecurity,
                s.FirstName,
                s.LastName,
                s.Gender,
                s.HighestDegree,
                s.ExternalYearsWorked,
                GROUP_CONCAT(DISTINCT dh.Department ORDER BY dh.StartDate SEPARATOR ', ') AS Departments,
                ph.Position,
                ph.Salary
            FROM
                Employees AS s
            LEFT JOIN
                EmployeeDepartments AS dh
                ON s.ID = dh.ID
            INNER JOIN
                EmployeePositions AS ph
                ON s.ID = ph.ID
        """

        # Build WHERE conditions
        conditions = []
        params = {}

        if fname:
            conditions.append("s.FirstName LIKE %(fname)s")
            params['fname'] = f"%{fname}%"
        if lname:
            conditions.append("s.LastName LIKE %(lname)s")
            params['lname'] = f"%{lname}%"
        if ssn:
            conditions.append("s.SocialSecurity = %(ssn)s")
            params['ssn'] = ssn
        if id:
            conditions.append("s.ID = %(id)s")
            params['id'] = id
        if phone:
            conditions.append("s.PhoneNumber = %(phone)s")
            params['phone'] = phone
        if gender:
            conditions.append("s.Gender = %(gender)s")
            params['gender'] = gender
        if degree:
            conditions.append("s.HighestDegree = %(degree)s")
            params['degree'] = degree
        if experience:
            conditions.append("s.ExternalYearsWorked = %(experience)s")
            params['experience'] = experience
        if position:
            conditions.append("ph.Position = %(position)s")
            params['position'] = position
        if employment_type:
            conditions.append("ph.EmploymentType = %(employment_type)s")
            params['employment_type'] = employment_type
        if departments:
            conditions.append("dh.Department IN %(departments)s")
            params['departments'] = departments
        if salary_min:
            conditions.append("ph.Salary >= %(salary_min)s")
            params['salary_min'] = salary_min
        if salary_max:
            conditions.append("ph.Salary <= %(salary_max)s")
            params['salary_max'] = salary_max
        if address:
            conditions.append("s.StreetAddress LIKE %(address)s")
            params['address'] = f"%{address}%"
        if city:
            conditions.append("s.City = %(city)s")
            params['city'] = city
        if state:
            conditions.append("s.State = %(state)s")
            params['state'] = state
        if zip_code:
            conditions.append("s.ZIPCode = %(zip_code)s")
            params['zip_code'] = zip_code

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += """
            GROUP BY
                s.ID, s.FirstName, s.LastName, s.Gender, s.BirthDate, s.SocialSecurity,
                s.PhoneNumber, s.StreetAddress, s.City, s.State, s.ZIPCode,
                s.HighestDegree, s.ExternalYearsWorked, ph.Position, ph.Salary
        """
        print(query)
        results = search_db(query, cursors.DictCursor, True, params)
        for row in results:
            row['SocialSecurity'] = f"***-**-{row['SocialSecurity'][-4:]}"

        positions_list = search_db('SELECT Name FROM Positions', cursors.DictCursor)
        departments_list = search_db('SELECT Name FROM Departments', cursors.DictCursor)
        genders_list = search_db('SELECT Name FROM Genders', cursors.DictCursor)
        degrees_list = search_db('SELECT Name FROM Degrees', cursors.DictCursor)
        return render_template('employee/search.html',
            employees=results,
            positions=positions_list,
            departments=departments_list,
            genders=genders_list,
            degrees=degrees_list
        )
    except Exception as e:
        print(e)
        flash('An error occurred while fetching the employees')
        return "Error", HTTPStatus.INTERNAL_SERVER_ERROR

@bp.get('/<int:id>')
def view(id):
    data = search_db('''
        SELECT
            s.ID,
            s.SocialSecurity,
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
            Employees AS s
        LEFT JOIN
            EmployeeDepartments AS dh
            ON s.ID = dh.ID
        INNER JOIN
            EmployeePositions AS ph
            ON s.ID = ph.ID
        WHERE
            s.ID = %s
        GROUP BY
            s.ID, s.FirstName, s.LastName, s.Gender, s.BirthDate, s.SocialSecurity,
            s.PhoneNumber, s.StreetAddress, s.City, s.State, s.ZIPCode,
            s.HighestDegree, s.ExternalYearsWorked, ph.Position, ph.Salary
    ''', cursors.DictCursor, False, (id,))
    if not data:
        return "Employee not found", HTTPStatus.NOT_FOUND
    return render_template('employee/view.html', employee=data)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    current_position = get_employee_position(id)
    current_departments = get_employee_departments(id)
    current_benefits = get_employee_benefits(id)
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
            # EmployeePositions data
            position = request.form['position']
            employment_type = request.form['employment_type']
            salary = request.form['salary']
            health_insurance = request.form['health_insurance']
            health_insurance_start_date = None
            if health_insurance == 'company':
                health_insurance_start_date = datetime.date(datetime.now())
            external_hire = request.form['external_hire']
            # EmployeeDepartments data
            selected_departments = request.form.getlist('departments')
            # Benefits data
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
                phone, degree, experience, id))

            if (current_position['Position'] != position
            or current_position['Salary'] != salary
            or current_position['EmploymentType'] != employment_type):
                # Remove records from active table
                cursor.execute('''
                    DELETE FROM EmployeePositions
                    WHERE ID = %s
                ''', (id,))
                # Insert updated information
                cursor.execute('''
                    INSERT INTO EmployeePositions (
                        ID, StartDate, Position, EmploymentType, Salary,
                        IsExternalHire, HealthCoverageStartDate
                    ) VALUES (%s, CURDATE(), %s, %s, %s, 0, %s)
                ''', (id, position, employment_type, salary,
                    health_insurance_start_date))

            # Update departments no longer associated with the employee
            for department in current_departments:
                if department not in selected_departments:
                    cursor.execute('''
                        DELETE FROM EmployeeDepartments
                        WHERE ID = %s AND Department = %s
                    ''', (id, department))

            # Add new departments
            for department in selected_departments:
                if department not in current_departments:
                    cursor.execute('''
                        INSERT INTO EmployeeDepartments (
                            ID, Department, StartDate
                        ) VALUES (%s, %s, CURDATE())
                    ''', (id, department))

            # Update benefits no longer associated with the employee
            for benefit in current_benefits:
                if benefit not in selected_benefits:
                    cursor.execute('''
                        UPDATE EmployeeBenefits
                        SET EndDate = CURDATE()
                        WHERE ID = %s AND Benefit = %s AND EndDate IS NULL
                    ''', (id, benefit))

            # Add new benefits
            for benefit in selected_benefits:
                if benefit not in current_benefits:
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
    benefits_list = search_db('SELECT Name FROM Benefits', cursors.DictCursor)
    positions_list = search_db('SELECT Name FROM Positions', cursors.DictCursor)
    departments_list = search_db('SELECT Name FROM Departments', cursors.DictCursor)
    genders_list = search_db('SELECT Name FROM Genders', cursors.DictCursor)
    degrees_list = search_db('SELECT Name FROM Degrees', cursors.DictCursor)

    emp['Departments'] = current_departments
    emp['Benefits'] = current_benefits
    emp['Salary'] = current_position['Salary']
    emp['Position'] = current_position['Position']
    return render_template('employee/form.html',
        emp=emp,
        positions=positions_list,
        departments=departments_list,
        benefits=benefits_list,
        degrees=degrees_list,
        genders=genders_list
    )

@bp.delete('<int:id>')
def archive_employee(id):
    try:
        emp = search_db('SELECT ID, LastName FROM Employees WHERE ID = %s',
            cursors.DictCursor, False, (id,))
        if not emp:
            return "Employee not found", HTTPStatus.NOT_FOUND
        db = open_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM EmployeeDepartments WHERE ID = %s", (id,))
        cursor.execute("DELETE FROM EmployeeBenefits WHERE ID = %s", (id,))
        cursor.execute("DELETE FROM EmployeePositions WHERE ID = %s", (id,))
        cursor.close()
        db.commit()
        close_db()
        # Rest of the data is deleted by cascade
        flash(f"Employee {emp['ID']} archived successfully")
        return "Success", HTTPStatus.OK
    except Exception as e:
        print(e)
        flash('An error occurred while deleting the employee')
        return "Error", HTTPStatus.INTERNAL_SERVER_ERROR


def get_employee_departments(id):
    current_departments = search_db('''
        SELECT Department FROM EmployeeDepartments WHERE ID = %s
    ''', cursors.Cursor, True, (id,))
    current_departments = [department[0] for department in current_departments]
    return current_departments

def get_employee_benefits(id):
    current_benefits = search_db('''
        SELECT Benefit FROM EmployeeBenefits WHERE ID = %s AND EndDate IS NULL
    ''', cursors.Cursor, True, (id,))
    current_benefits = [benefit[0] for benefit in current_benefits]
    return current_benefits

def get_employee_position(id):
    return search_db('''
        SELECT Salary, Position FROM EmployeePositions WHERE ID = %s
    ''', cursors.DictCursor, False, (id,))
