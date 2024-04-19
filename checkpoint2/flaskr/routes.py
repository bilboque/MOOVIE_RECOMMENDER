from flask import (jsonify, render_template,
                   request, session, Blueprint)
from db import get_db_connection

routes_bp = Blueprint('routes', __name__)


def get_session_key():
    try:
        with open('sessionkey.txt', 'r') as file:
            my_super_secret_key = file.readline().strip()
        return my_super_secret_key
    except FileNotFoundError:
        return None


routes_bp.secret_key = get_session_key()  # secret key for session management


@routes_bp.route("/")  # this will become the main page with movies displayed
def index():
    output = getIndex()
    return render_template('app.html', output=output)


@routes_bp.route("/api")
def getIndex():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    mysql_query = """ SELECT * FROM entries LIMIT 10;"""
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    # return jsonify(output)
    return output


@routes_bp.route("/about/")
def about():
    return "<h3>This is an IMDb project; codename DBMi</h3>"


# route for displaying test data
@routes_bp.route("/movies/", methods=['GET'])
def movies():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    mysql_query = """ SHOW TABLES;"""
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    return jsonify(output)
    # return str(output)


@routes_bp.route("/api/movies/", methods=['GET'])
def getMovies():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    mysql_query = """SHOW title FROM entries LIMIT 10;"""
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    return jsonify(output)


# view movie details


@routes_bp.route("/api/movies/<int:movie_id>", methods=['GET'])
def getMovieDetails(movie_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM entries WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()
    if movie:
        return jsonify(movie), 200
    else:
        return jsonify({"error": "Movie not found"}), 404


@routes_bp.route("/search")
def search():
    search = getIndex()
    return render_template('app.html', search=search)


@routes_bp.route('/api/search', methods=['GET'])  # search for a movie
def search_movie():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = request.args.get('query')
    cursor.execute("SELECT * FROM entries WHERE title LIKE %s",
                   ('%' + query + '%',))
    output = cursor.fetchall()
    if output:
        return render_template('app.html', output=output)
    else:
        return jsonify({"message": "No movies found"}), 404


# Watchlist route
@routes_bp.route('/watchlist', methods=['GET'])
# @login_required  # decorator to ensure that only authenticated users can access the route
def view_watchlist():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user_id = session['user_id']

    cursor.execute(
        "SELECT * watchlist where id = %s", (user_id))
    watchlist = cursor.fetchall()

    if watchlist:
        return jsonify(watchlist), 200
    else:
        return jsonify({"message": "Watchlist is empty"}), 404
