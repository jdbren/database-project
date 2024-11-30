import MySQLdb
from flask import current_app, g

def open_db():
    if 'db' not in g:
        g.db = MySQLdb.connect(
            current_app.config['MYSQL_HOST'],
            current_app.config['MYSQL_USER'],
            current_app.config['MYSQL_PASSWORD'],
            current_app.config['MYSQL_DB']
        )

    return g.db

def close_db(e=None):
    db = g.pop('db', e)

    if db is not None:
        db.close()

def modify_db(query: str, args=None):
    db = open_db()
    cursor = db.cursor()

    try:
        cursor.execute(query, args)
        db.commit()
    except MySQLdb.Error:
        db.rollback()
        raise
    finally:
        cursor.close()
        close_db()

def search_db(query: str, cursor_type, multi=True, args=None):
    db = open_db()
    cursor = db.cursor(cursor_type)

    try:
        cursor.execute(query, args)
        if not multi:
            return cursor.fetchone()
        else:
            return cursor.fetchall()
    finally:
        cursor.close()
        close_db()

def init_db(app):
    app.teardown_appcontext(close_db)
