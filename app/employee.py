import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
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
            employee_number = request.form['employee_number']
            name = request.form['name']
            dob = request.form['dob']
            address = request.form['address']
            phone = request.form['phone']
            degree = request.form['degree']
            experience = request.form['experience']
            hiring_position = request.form['hiring_position']
            hiring_salary = request.form['hiring_salary']
            current_position = request.form['current_position']
            current_salary = request.form['current_salary']

            # Insert data into the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO employees (
                    ssn, employee_number, name, dob, address, phone,
                    degree, experience, hiring_position, hiring_salary,
                    current_position, current_salary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ssn, employee_number, name, dob, address, phone,
                degree, experience, hiring_position, hiring_salary,
                current_position, current_salary
            ))
            db.commit()
            close_db()

            return "Submitted!", 201

        except Exception as e:
            return "Error", 500

    return render_template('employee/insert.html')



@bp.route('/search', methods=('GET',))
def search():
    return render_template('employee/search.html')

@bp.route('/<int:id>', methods=('GET', 'PUT', 'DELETE'))
def update(id):
    return ""
