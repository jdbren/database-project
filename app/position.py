from http import HTTPStatus
from MySQLdb import cursors
from flask import Blueprint, render_template, redirect, request, url_for
from app.db import search_db, modify_db, open_db, close_db

bp = Blueprint('position', __name__, url_prefix='/position')

@bp.route('insert', methods=('GET', 'POST'))
def insert_position():
    if request.method == 'POST':
        name = request.form['name']
        salary_min = request.form['salary_min']
        salary_max = request.form['salary_max']

        try:
            db = open_db()
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO Positions (
                    Name, MinimumSalary, MaximumSalary
                ) VALUES (%s, %s, %s)
            ''', (name, salary_min, salary_max))
            db.commit()
            cursor.close()
            close_db(db)
            return redirect(url_for('position.search_position'))
        except Exception as e:
            close_db(db)
            print(e)
            return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

    return render_template('position/form.html')

@bp.route('/<path:position>/edit', methods=('GET', 'POST'))
def update_position(position):
    position = search_db('SELECT * FROM Positions WHERE Name = %s',
        cursors.DictCursor, False, (position,))
    if not position:
        return 'Position not found', HTTPStatus.NOT_FOUND

    if request.method == 'POST':
        name = request.form['name']
        salary_min = request.form['salary_min']
        salary_max = request.form['salary_max']

        try:
            db = open_db()
            cursor = db.cursor()
            cursor.execute('''
                UPDATE Positions
                SET Name = %s, MinimumSalary = %s, MaximumSalary = %s
                WHERE Name = %s
            ''', (name, salary_min, salary_max, position['Name']))
            db.commit()
            cursor.close()
            close_db(db)
            return redirect(url_for('position.search_position'))
        except Exception as e:
            close_db(db)
            print(e)
            return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

    return render_template('position/form.html', pos=position)

@bp.get('search')
def search_position():
    order = 'Name'
    if request.args.get('order') == 'avg_salary':
        order = 'AverageSalary DESC'
    pos_list = search_db(f'''
        SELECT Name, MinimumSalary, MaximumSalary,
            COUNT(ep.ID) AS EmployeeCount,
            ROUND(AVG(Salary)) AS AverageSalary,
            ROUND(AVG(CASE WHEN e.Gender = 'Male' THEN ep.Salary END)) AS AvgSalaryMale,
            ROUND(AVG(CASE WHEN e.Gender = 'Female' THEN ep.Salary END)) AS AvgSalaryFemale
        FROM Positions
        LEFT JOIN EmployeePositions ep
            ON Position = Name
        JOIN Employees e ON e.ID = ep.ID
        GROUP BY Name
        ORDER BY {order} 
    ''', cursors.DictCursor)
    return render_template('position/search.html', positions=pos_list)
