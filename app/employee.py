import functools

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from app.db import get_db, close_db

bp = Blueprint('employee', __name__, url_prefix='/employee')

@bp.route('/')
def index():
    return render_template('employee/index.html')


## TODO: Update once schema is finalized
@bp.route('/insert', methods=('GET', 'POST'))
def insert():
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
            degree = request.form['degree']
            experience = request.form['experience']
            # position = request.form['position']
            # salary = request.form['salary']

            print(ssn, fname, dob, phone, degree, experience)

            # Insert data into the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO Staff (
                    SocialSecurity, FirstName, LastName, Gender, BirthDate,
                    StreetAddress, City, State, ZIPCode, PhoneNumber,
                    ExternalYearsWorked
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                ssn, fname, lname, gender, dob, address, city, state, zip,
                phone, experience
            ))
            cursor.close()
            db.commit()
            close_db()

            return redirect('/employee', 201)

        except Exception as e:
            print(e)
            return "Error", 500

    return render_template('employee/insert.html')



@bp.route('/search', methods=('GET',))
def search():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM Staff')
    employees = cursor.fetchall()
    cursor.close()

    print(employees)

    close_db()

    return render_template('employee/search.html', employees=employees)

@bp.route('/<int:id>', methods=('GET', 'PUT', 'DELETE'))
def update(id):
    return render_template('employee/update.html')
