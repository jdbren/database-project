from MySQLdb import cursors
from flask import Blueprint, render_template, request
from app.db import search_db

bp = Blueprint('department', __name__, url_prefix='/department')

@bp.get('/search')
def search_department():
    departments_list = search_db('SELECT Name FROM Departments', cursors.DictCursor)
    selected_department = request.args.get('department')
    if not selected_department:
        return render_template('department/search.html', dept_list=departments_list, args=request.args)

    table = 'EmployeeDepartmentsHistory' if request.args.get('history') else 'EmployeeDepartments'

    query = "SELECT e.ID, CONCAT(e.FirstName, ' ', e.LastName) AS Name, ed.StartDate "
    if request.args.get('history'):
        query += ', ed.EndDate '
    query += f' FROM Employees e NATURAL JOIN {table} ed '

    if selected_department:
        query += f'WHERE ed.Department = \'{selected_department}\''
    if request.args.get('start_date'):
        query += f' AND ed.StartDate >= \'{request.args.get("start_date")}\''
    if request.args.get('end_date'):
        query += f' AND ed.EndDate <= \'{request.args.get("end_date")}\''
    query += ' ORDER BY ed.StartDate'

    print(query)

    results = search_db(query, cursors.DictCursor)
    return render_template('department/search.html', dept_list=departments_list,
                           args=request.args, dept=selected_department,
                           employees=results)
