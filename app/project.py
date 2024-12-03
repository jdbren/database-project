from http import HTTPStatus
import datetime
from MySQLdb import cursors
from flask import Blueprint, render_template, redirect, request, url_for
from app.db import search_db, modify_db, open_db, close_db

bp = Blueprint('project', __name__, url_prefix='/project')

@bp.route('/')
def index():
    return render_template('project/index.html')

@bp.route('/insert', methods=('GET', 'POST'))
def insert_project():
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        leader = request.form['leader']
        employees = []
        employee_ids = request.form.getlist('employee_id')  # List of employee IDs
        roles = request.form.getlist('role')               # Corresponding roles
        for emp_id, role in zip(employee_ids, roles):
            employees.append({'employee_id': emp_id, 'role': role})

        try:
            db = open_db()
            cursor = db.cursor()
            cursor.callproc("CreateProject", (name, department, leader, datetime.date.today()))

            cursor.execute('SELECT LAST_INSERT_ID()')
            project_id = cursor.fetchone()[0]

            params = [(project_id, emp['employee_id'], emp['role']) for emp in employees]
            cursor.executemany('''
                INSERT INTO EmployeeRoles (
                    ProjectID, EmployeeID, StartDate, Role
                )
                VALUES (%s, %s, CURDATE(), %s)
            ''', params)
            db.commit()
            cursor.close()
            close_db(db)

            return redirect(url_for('project.index'))
        except Exception as e:
            close_db()
            print(e)
            return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

    departments = search_db('SELECT Name FROM Departments', cursors.DictCursor)
    project_status = search_db('SELECT Name FROM ProjectStatus', cursors.DictCursor)
    roles = search_db('SELECT Name FROM ProjectRoles', cursors.DictCursor)
    return render_template('project/form.html',
        depts=departments, statuses=project_status,
        roles=roles)


@bp.get('/search')
def search_project():
    departments_list = search_db('SELECT Name FROM Departments', cursors.DictCursor)
    project_status_list = search_db('SELECT Name FROM ProjectStatus', cursors.DictCursor)
    name = request.args.get('name')
    id = request.args.get('id')
    department = request.args.get('department')
    status = request.args.get('status')
    leader = request.args.get('leader')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = '''
        SELECT p.ID, p.Name, p.Department, p.Status,
            CONCAT(e.FirstName, ' ', e.LastName) AS Leader,
            GROUP_CONCAT(CONCAT(emp.FirstName, ' ', emp.LastName, ' (', er.Role, ')') SEPARATOR ', ') AS Employees
        FROM Projects p
        JOIN Employees e ON p.Leader = e.ID
        LEFT JOIN EmployeeRoles er ON p.ID = er.ProjectID
        LEFT JOIN Employees emp ON er.EmployeeID = emp.ID
    '''

    conditions = []
    params = {}
    if name:
        conditions.append('p.Name LIKE %(name)s')
        params['name'] = f'%{name}%'
    if id:
        conditions.append('p.ID = %(id)s')
        params['id'] = id
    if department:
        conditions.append('p.Department = %(department)s')
        params['department'] = department
    if status:
        conditions.append('p.Status = %(status)s')
        params['status'] = status
    if leader:
        conditions.append('p.Leader = %(leader)s')
        params['leader'] = leader

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' GROUP BY p.ID'

    print(query)

    try:
        projects = search_db(query, cursors.DictCursor, True, params)
    except Exception as e:
        print(e)
        return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

    for project in projects:
        if project['Employees']:
            employee_list = project['Employees'].split(', ')
            if len(employee_list) > 2:
                project['Employees'] = ', '.join(employee_list[:2]) + ', ...'

    return render_template('project/search.html',
        depts=departments_list, statuses=project_status_list,
        projects=projects, args=request.args)

@bp.get('<int:project_id>')
def view_project(project_id):
    # Fetch project details
    query_project = '''
        SELECT p.ID, p.Name, p.Department, p.Status,
               CONCAT(e.FirstName, ' ', e.LastName) AS Leader
        FROM Projects p
        JOIN Employees e ON p.Leader = e.ID
        WHERE p.ID = %(project_id)s
    '''
    project = search_db(query_project, cursors.DictCursor, False, {'project_id': project_id})

    # Fetch employees working on this project
    query_employees = '''
        SELECT er.EmployeeID, CONCAT(emp.FirstName, ' ', emp.LastName) AS Name,
               er.Role, er.StartDate
        FROM EmployeeRoles er
        JOIN Employees emp ON er.EmployeeID = emp.ID
        WHERE er.ProjectID = %(project_id)s
    '''
    employees = search_db(query_employees, cursors.DictCursor, True, {'project_id': project_id})

    return render_template('project/view.html', project=project, employees=employees)


@bp.route('<int:id>/edit', methods=('GET', 'POST'))
def update_project(id):
    project = search_db('SELECT * FROM Projects WHERE ID = %s', cursors.DictCursor, False, (id,))
    current_roles = get_employees_by_project(id)

    if not project:
        return 'Project not found', HTTPStatus.NOT_FOUND
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        leader = request.form['leader']
        status = request.form['status']
        employees = []
        employee_ids = request.form.getlist('employee_id')  # List of employee IDs
        new_roles = request.form.getlist('role')               # Corresponding roles
        for emp_id, role in zip(employee_ids, new_roles):
            employees.append(dict(employee_id=int(emp_id), role=role))

        try:
            db = open_db()
            cursor = db.cursor()
            if project['Status'] == 'Closed':
                if status == 'In Progress':
                    cursor.callproc('ReviveProject',
                        (id, datetime.date.today(), leader))
                else:
                    return "Cannot modify closed project", HTTPStatus.BAD_REQUEST
            if project['Name'] != name or project['Department'] != department:
                cursor.execute('''
                    UPDATE Projects
                    SET Name = %s, Department = %s
                    WHERE ID = %s
                ''', (name, department, id))
            if leader != project['Leader']:
                cursor.callproc('ChangeProjectLeader', (id, leader, datetime.date.today()))
            for emp in employees:
                if emp['employee_id'] not in [role['EmployeeID'] for role in current_roles]:
                    cursor.execute('''
                        INSERT INTO EmployeeRoles (
                            ProjectID, EmployeeID, StartDate, Role
                        )
                        VALUES (%s, %s, CURDATE(), %s)
                    ''', (id, emp['employee_id'], emp['role']))
                else:
                    cursor.execute('''
                        UPDATE EmployeeRoles
                        SET Role = %s
                        WHERE ProjectID = %s AND EmployeeID = %s
                    ''', (emp['role'], id, emp['employee_id']))
            for role in current_roles:
                if role['EmployeeID'] not in [emp['employee_id'] for emp in employees]:
                    cursor.callproc("RetireFromRole", (role['EmployeeID'], id, datetime.date.today()))
            if status != project['Status']:
                if status == 'Closed':
                    cursor.callproc("CloseProject", (id, datetime.date.today()))
                else:
                    cursor.execute('UPDATE Projects SET Status = %s WHERE ID = %s', (status, id))
            db.commit()
            cursor.close()
            close_db(db)
            return redirect(url_for('project.search_project'))
        except Exception as e:
            close_db(db)
            print(e)
            return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

    departments = search_db('SELECT Name FROM Departments', cursors.DictCursor)
    status_list = search_db('SELECT Name FROM ProjectStatus', cursors.DictCursor)
    roles = search_db('SELECT Name FROM ProjectRoles', cursors.DictCursor)
    return render_template('project/form.html',
        proj=project,
        depts=departments,
        statuses=status_list,
        roles=roles,
        emps=current_roles
    )

@bp.delete('/<int:id>')
def delete_project(id):
    return ""

def get_employees_by_project(project_id):
    return search_db('''
        SELECT er.EmployeeID, er.Role
        FROM EmployeeRoles er
        WHERE er.ProjectID = %s
    ''', cursors.DictCursor, True, (project_id,))
