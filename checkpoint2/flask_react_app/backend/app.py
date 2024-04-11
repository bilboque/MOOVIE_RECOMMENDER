from flask import Flask, jsonify
# from flask_mysql_connector import MySQL
# from mysql_connector_python import connector
# from mysql import connector
import mysql.connector  # this works

app = Flask(__name__)
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_DATABASE'] = 'DBMi'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_PORT'] = 3306
# mysql = MySQL(app)

# create db connection
connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="podmanroot13",
    database="DBMi"  # db name to access
)


cursor = connection.cursor()


@app.route("/")  # this will become the main page with movies displayed
def hello_world():
    # mysql_query = """ SELECT title FROM entries """
    # cursor.execute(mysql_query)
    # output = cursor.fetchall()
    # return jsonify(output)
    return "<p>Hello, World!</p>"


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
