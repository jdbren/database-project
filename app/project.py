from http import HTTPStatus
from datetime import datetime
from MySQLdb import cursors
from flask import ( Blueprint, render_template,
    redirect, request, url_for
)
from app.db import (
    search_db, modify_db, open_db, close_db
)

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
            cursor.callproc("CreateProject", (name, department, leader, datetime.date(datetime.now())))

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
            print(e)
            return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

    departments = search_db('SELECT Name FROM Departments', cursors.DictCursor)
    project_status = search_db('SELECT Name FROM ProjectStatus', cursors.DictCursor)
    roles = search_db('SELECT Name FROM ProjectRoles', cursors.DictCursor)
    return render_template('project/form.html',
        depts=departments, statuses=project_status,
        roles=roles)


@bp.route('/search', methods=('GET',))
def search_project():
    departments_list = search_db('SELECT Name FROM Departments', cursors.DictCursor)
    project_status_list = search_db('SELECT Name FROM ProjectStatus', cursors.DictCursor)
    name = request.args.get('name')
    department = request.args.get('department')
    status = request.args.get('status')
    leader = request.args.get('leader')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = '''
        SELECT p.ID, p.Name, p.Department, p.Status,
            CONCAT(e.FirstName, ' ', e.LastName) as Leader
        FROM Projects p
        JOIN Employees e ON p.Leader = e.ID
    '''

    conditions = []
    params = {}
    if name:
        conditions.append('p.Name = %(name)s')
        params['name'] = name
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

    projects = search_db(query, cursors.DictCursor, True, params)

    return render_template('project/search.html',
        depts=departments_list, statuses=project_status_list,
        projects=projects)

@bp.get('/<int:id>')
def get_project(id):
    return ""

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
            employees.append({'employee_id': emp_id, 'role': role})

        try:
            db = open_db()
            cursor = db.cursor()
            if project['Status'] == 'Closed':
                if status == 'In Progress':
                    cursor.callproc('ReviveProject',
                        (id, datetime.date(datetime.now()), leader))
                else:
                    return "Cannot modify closed project", HTTPStatus.BAD_REQUEST
            if project['Name'] != name or project['Department'] != department:
                cursor.execute('''
                    UPDATE Projects
                    SET Name = %s, Department = %s
                    WHERE ID = %s
                ''', (name, department, id))
            if leader != project['Leader']:
                cursor.callproc('ChangeProjectLeader', (id, leader, datetime.date(datetime.now())))
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
                    cursor.execute('''
                        DELETE FROM EmployeeRoles
                        WHERE ProjectID = %s AND EmployeeID = %s
                    ''', (id, role['EmployeeID']))
            if status != project['Status']:
                if status == 'Closed':
                    cursor.execute('CALL CloseProject (%s, CURDATE())', (id,))
                else:
                    cursor.execute('UPDATE Projects SET Status = %s WHERE ID = %s', (status, id))
            db.commit()
            cursor.close()
            close_db(db)
            return redirect(url_for('project.search_project'))
        except Exception as e:
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
