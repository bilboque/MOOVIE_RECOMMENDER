import mysql.connector
from flask import Blueprint

db_blueprint = Blueprint('db', __name__)


def read_db_password():
    try:
        with open('password.txt', 'r') as file:
            password = file.readline().strip()  # Assuming password is stored in a single line
        return password
    except FileNotFoundError:
        return None


def get_db_connection():
    # create db connection
    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=read_db_password(),
        database="DBMi"  # db name to access
    )
    return connection

    # cursor = connection.cursor()
