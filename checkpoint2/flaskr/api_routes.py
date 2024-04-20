from flask import (jsonify, render_template,
                   request, session, Blueprint)
from db import get_db_connection

api_bp = Blueprint('api_routes', __name__)


@api_bp.route("/api")
def getIndex():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    mysql_query = """ SELECT * FROM entries LIMIT 10;"""
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    cursor.close()
    connection.close()

    # return jsonify(output)
    return output


@api_bp.route("/api/movies/", methods=['GET'])
def getMovies():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    mysql_query = """SHOW title FROM entries LIMIT 10;"""
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(output)


@api_bp.route("/api/movies/<int:movie_id>", methods=['GET'])
def getMovieDetails(movie_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM entries WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    connection.close()
    return movie


@api_bp.route('/api/search', methods=['GET'])  # search for a movie
def searchEntry(query):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM entries WHERE title LIKE %s",
                   ('%' + query + '%',))
    output = cursor.fetchall()
    cursor.close()
    connection.close()
    return output
