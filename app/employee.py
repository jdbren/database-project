import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from app.db import get_db, close_db

bp = Blueprint('employee', __name__, url_prefix='/employee')

@bp.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM employee')
    emp = cursor.fetchall()
    close_db()
    return render_template('employee/index.html', emp=emp)

@bp.route('/insert', methods=('GET', 'POST'))
def insert():
    return "insert"

@bp.route('<int:id>/update', methods=('GET', 'POST'))
def update(id):
    return "update"

# @bp.route('<int:id>/delete', methods=('POST'))
# def delete(id):
#     return "delete"
