import MySQLdb

from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = MySQLdb.connect(
            current_app.config['MYSQL_HOST'],
            current_app.config['MYSQL_USER'],
            current_app.config['MYSQL_PASSWORD'],
            current_app.config['MYSQL_DB']
        )
        g.db.row_factory = MySQLdb.cursors.DictCursor

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def execute_and_commit(query: str, args=None):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, args)
    cursor.close()
    db.commit()
    close_db()
    return

def execute_and_fetchone(query: str, cursor_type, args=None):
    db = get_db()
    cursor = db.cursor(cursor_type)
    cursor.execute(query, args)
    result = cursor.fetchone()
    cursor.close()
    close_db()
    return result

def execute_and_fetchall(query: str, cursor_type, args=None):
    db = get_db()
    cursor = db.cursor(cursor_type)
    cursor.execute(query, args)
    result = cursor.fetchall()
    cursor.close()
    close_db()
    return result

def init_db(app):
    app.teardown_appcontext(close_db)
