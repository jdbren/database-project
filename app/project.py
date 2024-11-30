from datetime import datetime
from http import HTTPStatus
from MySQLdb import cursors
from flask import ( Blueprint, render_template,
    flash, redirect, request, session, url_for
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
    return ""

@bp.route('/search', methods=('GET',))
def search_project():
    return ""

@bp.get('/<int:id>')
def get_project(id):
    return ""

@bp.route('<int:id>/edit', methods=('GET', 'POST'))
def update_project(id):
    return ""

@bp.delete('/<int:id>')
def delete_project(id):
    return ""
