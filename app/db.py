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

def init_app(app):
    app.teardown_appcontext(close_db)
