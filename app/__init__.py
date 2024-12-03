import os
from flask import Flask, render_template

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        MYSQL_HOST = 'localhost',
        MYSQL_USER = 'root',
        MYSQL_PASSWORD = os.getenv("DB_PASSWORD"),
        MYSQL_DB = 'company'
    )

    from . import db
    db.init_db(app)

<<<<<<< HEAD
<<<<<<< HEAD
    from . import employee, project, department, position, query
    app.register_blueprint(employee.bp)
    app.register_blueprint(project.bp)
    app.register_blueprint(department.bp)
    app.register_blueprint(position.bp)
=======
    from . import employee, project, department, query
    app.register_blueprint(employee.bp)
    app.register_blueprint(project.bp)
    app.register_blueprint(department.bp)
>>>>>>> 975bb0e (implement search for departments history)
=======
    from . import employee, project, department, position, query
    app.register_blueprint(employee.bp)
    app.register_blueprint(project.bp)
    app.register_blueprint(department.bp)
    app.register_blueprint(position.bp)
>>>>>>> 7442c02 (fix dates)
    app.register_blueprint(query.bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
