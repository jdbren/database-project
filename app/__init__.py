import os
from flask import Flask, render_template

def create_app():
    # Create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        MYSQL_HOST = 'localhost',
        MYSQL_USER = 'GenericApplication',
        MYSQL_PASSWORD = os.getenv("DB_PASSWORD", ""),
        MYSQL_DB = 'GenericCompany'
    )

    from . import db
    db.init_db(app)

    from . import employee, project, department, position, query
    app.register_blueprint(employee.bp)
    app.register_blueprint(project.bp)
    app.register_blueprint(department.bp)
    app.register_blueprint(position.bp)
    app.register_blueprint(query.bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
