from MySQLdb import cursors
from flask import Blueprint, render_template, request
from app.db import search_db

bp = Blueprint('department', __name__, url_prefix='/department')

@bp.get('<path:department>')
def department_info(department):
    selected_department = department
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
    return render_template('department/view.html',
                           dept=selected_department,
                           employees=results,
                           history=bool(request.args.get('history')))

@bp.get('search')
def search_department():
    dept_list = search_db('SELECT Name FROM Departments', cursors.DictCursor)
    dept_table = 'EmployeeDepartmentsHistory' if request.args.get('history') else 'EmployeeDepartments'
    pos_table = 'EmployeePositionsHistory' if request.args.get('history') else 'EmployeePositions'
    order_by = request.args.get('order_by', 'Department')
    asc = request.args.get('order', 'ASC')

    query = f'''
        SELECT ed.Department,
            COUNT(ed.ID) AS NumEmployees,
            ROUND(AVG(ep.Salary)) AS AvgSalary,
            MIN(ed.StartDate) AS EarliestStartDate
        FROM {dept_table} ed
        JOIN {pos_table} ep ON ed.ID = ep.ID
        GROUP BY ed.Department
        ORDER BY {order_by} {asc}
    '''

    departments = search_db(query, cursors.DictCursor)
    return render_template('department/search.html', dept_list=dept_list, departments=departments, args=request.args)
