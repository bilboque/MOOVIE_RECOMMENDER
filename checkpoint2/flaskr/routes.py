from flask import (jsonify, render_template,
                   request, session, Blueprint, url_for, redirect)
from db import get_db_connection
from api_routes import (getIndex, getMovies, searchEntry,
                        getMovieDetails, view_watchlist, api_add_to_watchlist)
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


@routes_bp.route('/moviedetails', methods=['GET'])
def movieDetails(id):
    details = getMovieDetails(id)
    return render_template('app.html', output=details)


@routes_bp.route('/watchlist', methods=['GET'])
def viewWatchlist():
    watchlist = view_watchlist()
    return render_template('app.html', output=watchlist)


@routes_bp.route('/add', methods=['POST'])
def add_to_watchlist():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    movie_id = request.form.get('entries_id')

    status = api_add_to_watchlist(user_id, movie_id)
    if status:
        return render_template('app.html', bool=status)
    else:
        return render_template('app.html', bool=status)
