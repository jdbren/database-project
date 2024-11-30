import os
from flask import Flask, render_template

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MYSQL_HOST = 'localhost',
        MYSQL_USER = 'root',
        MYSQL_PASSWORD = os.getenv("DB_PASSWORD"),
        MYSQL_DB = 'company'
    )

    from . import db
    db.init_db(app)

    from . import employee
    app.register_blueprint(employee.bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
