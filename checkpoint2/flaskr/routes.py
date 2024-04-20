from flask import (jsonify, render_template,
                   request, session, Blueprint)
from db import get_db_connection
from api_routes import getIndex, getMovies, searchEntry, getMovieDetails
routes_bp = Blueprint('routes', __name__)


@routes_bp.route("/")
def index():
    output = getIndex()
    return render_template('app.html', output=output)


@routes_bp.route("/about")
def about():
    return "<h3>This is an IMDb project; codename DBMi</h3>"


# route for displaying test data
@routes_bp.route("/movies", methods=['GET'])
def movies():
    output = getMovies()
    return render_template('app.html', output=output)
    # return str(output)


@routes_bp.route("/search")
def search():
    query = request.args.get('query')
    search = searchEntry(query)
    return render_template('app.html', output=search)


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
    cursor.close()
    connection.close()

    if watchlist:
        return jsonify(watchlist), 200
    else:
        return jsonify({"message": "Watchlist is empty"}), 404


@routes_bp.route('/moviedetails', methods=['GET'])
def movieDetails(id):
    details = getMovieDetails(id)
    return render_template('app.html', output=details)
