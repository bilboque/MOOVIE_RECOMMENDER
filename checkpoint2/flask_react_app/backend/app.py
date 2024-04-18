from flask import Flask, jsonify, render_template

import mysql.connector  # this works

app = Flask(__name__)


def read_db_password():
    try:
        with open('password.txt', 'r') as file:
            password = file.readline().strip()  # Assuming password is stored in a single line
        return password
    except FileNotFoundError:
        return None


# create db connection
connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=read_db_password(),
    database="DBMi"  # db name to access
)


cursor = connection.cursor()


@app.route("/")  # this will become the main page with movies displayed
def hello_world():
    # mysql_query = """ SELECT title FROM entries """
    # cursor.execute(mysql_query)
    # output = cursor.fetchall()
    # return jsonify(output)
    return render_template('app.html')


@app.route("/about/")
def about():
    return "<h3>This is an IMDb project; codename DBMi</h3>"


# route for displaying test data
@app.route("/movies/", methods=['GET'])
def movies():
    mysql_query = """ SHOW TABLES;"""
    # conn = mysql.connection
    # cur = conn.cursor()
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    return str(output)
    # return str(output)


if __name__ == '__main__':
    app.run(debug=True)
