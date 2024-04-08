from flask import Flask, jsonify
from mysql import connector


app = Flask(__name__)

# create db connection
connection = connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="",
    database="DBMi"  # db name to access
)


cursor = connection.cursor()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/about/")
def about():
    return "<h3>This is an IMDb project; codename DBMi</h3>"


# route for displaying test data
@app.route("/movies/")
def movies():
    mysql_query = """ SELECT * FROM movies"""
    cursor.execute(mysql_query)
    movies = cursor.fetchall()
    result = {}
    result["data"] = []

    for movie in movies:
        dict = {}
        dict["id"] = movie[0]
        dict["title"] = movie[1]

        result["data"].append(dict)

    return jsonify(result)
