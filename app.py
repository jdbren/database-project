import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_mysqldb import MySQL

load_dotenv()

app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD")
app.config['MYSQL_DB'] = 'company'

mysql = MySQL(app)


@app.route('/')
def home():
    connection = mysql.connection
    if connection is None:
        return "No connection"
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Employee")
    emp = cursor.fetchone()
    return render_template('employee.html', emp=emp)
