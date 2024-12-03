from flask import Blueprint, render_template, flash, request
from app.db import open_db, close_db

bp = Blueprint('query', __name__, url_prefix='/query')

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'GET':
        return render_template('query/index.html')

    query = request.form['query']
    try:
        db = open_db()
        cursor = db.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        cursor.close()
    except Exception as e:
        flash(f"An error occurred: {e}", 'error')
        return render_template('query/index.html', query=query)
    finally:
        close_db()
    return render_template('query/results.html', query=query, rows=results, cols=column_names)
