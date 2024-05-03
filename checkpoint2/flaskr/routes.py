from flask import (render_template,
                   request, session, Blueprint, url_for, redirect)
from api_routes import (getIndex, getMovies, searchEntry,
                        getMovieDetails, view_watchlist, api_add_to_watchlist,
                        api_remove_from_watchlist, getCategories,
                        get_specific_category)
import requests

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


@routes_bp.route('/movie/<int:entries_id>', methods=['GET'])
def movieDetails(entries_id):
    details = getMovieDetails(entries_id)
    print(details)
    similarMovies = requests.get(
        "/api/recommendation", header={"args": details['title']})
    return render_template('movie_details.html', output=details, output2=similarMovies)


@routes_bp.route('/watchlist', methods=['GET'])
def viewWatchlist():
    watchlist = view_watchlist()
    return render_template('watchlist.html', output=watchlist)


@routes_bp.route('/add/<int:entries_id>', methods=['POST'])
def add_to_watchlist(entries_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    status = api_add_to_watchlist(user_id, entries_id)
    output = getIndex()
    return render_template('app.html', output=output)


@routes_bp.route('/remove/<int:entries_id>', methods=['POST'])
def remove_from_watchlist(entries_id):
    user_id = session['user_id']
    api_remove_from_watchlist(user_id, entries_id)
    watchlist = view_watchlist()
    return render_template('watchlist.html', output=watchlist)


@routes_bp.route('/category', methods=['GET'])
def categories():
    output = getCategories()
    return render_template('categories.html', output=output)


@routes_bp.route('/category/<category>', methods=['GET'])
def specific_category():
    output = get_specific_category()
    return render_template('categories.html', output=output)
