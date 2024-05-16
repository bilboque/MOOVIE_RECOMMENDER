from flask import (render_template,
                   request, session, Blueprint, url_for, redirect,
                   jsonify)

from api_routes import (getIndex, searchEntry,
                        getMovieDetails, view_watchlist, api_add_to_watchlist,
                        api_remove_from_watchlist, getCategories,
                        get_specific_category, getSimilarMovieDetails,
                        getRecommendations, api_review)
import requests
import json

routes_bp = Blueprint('routes', __name__)


@routes_bp.route("/")
def index():
    output = getIndex()
    return render_template('app.html', output=output)


@routes_bp.route("/about")
def about():
    return "<h3>This is an IMDb project; codename DBMi</h3>"


@routes_bp.route("/search")  # perform a normal search
def search():
    query = request.args.get('query')
    search = searchEntry(query)
    return render_template('app.html', output=search)


@routes_bp.route("/advancedsearch")  # perform an advanced search
def advanced_search():
    query = request.args.get('query')
    if query:
        advance = requests.get("http://127.0.0.1:5000/api/recommendation",
                               headers={"args": query})
        advancedSearch = advance.text
        result = getSimilarMovieDetails(json.loads(advancedSearch))
        print(result)
    else:
        print("nothing found in advanced search")
        result = []
    return render_template('advanced.html', output=result)


# display further information on a movie
@routes_bp.route('/movie/<int:entries_id>')
def movieDetails(entries_id):
    details = getMovieDetails(entries_id)

    # get movie recommendations
    # similar = getRecommendations(details['title'])
    similarMovies = requests.get(
        "http://127.0.0.1:5000/api/recommendation",
        headers={"args": details['title']})  # this returns a byte string

    similarContent = similarMovies.text
    similar = json.loads(similarContent)  # parses string as list

    similarMovieDetails = getSimilarMovieDetails(similar)
    reviews = get_review(entries_id)
    # print(similarMovieDetails)

    return render_template('movie_details.html', output=details,
                           output2=similarMovieDetails)


@routes_bp.route('/watchlist')  # display watchlist
def viewWatchlist():
    watchlist = view_watchlist()
    movies = []
    for movie in watchlist:
        movies.append(movie['title'])

    movie_titles = ', '.join(movies)
    similarMovies = requests.get(
        "http://127.0.0.1:5000/api/recommendation",
        headers={"args": movie_titles})  # this returns a byte string

    similarContent = similarMovies.text
    similar = json.loads(similarContent)  # parses string as list

    similarMovieDetails = getSimilarMovieDetails(similar)

    return render_template('watchlist.html', output=watchlist, output2=similarMovieDetails)


# add movie to watchlist
@routes_bp.route('/add/<int:entries_id>', methods=['POST'])
def add_to_watchlist(entries_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    api_add_to_watchlist(user_id, entries_id)
    output = getIndex()
    return render_template('app.html', output=output)


# remove movie from watchlist
@routes_bp.route('/remove/<int:entries_id>', methods=['POST'])
def remove_from_watchlist(entries_id):
    user_id = session['user_id']
    api_remove_from_watchlist(user_id, entries_id)
    watchlist = view_watchlist()
    return render_template('watchlist.html', output=watchlist)


@routes_bp.route('/category')
def categories():
    output = getCategories()
    return render_template('categories.html', output=output)


@routes_bp.route('/category/<category>')
def specific_category():
    output = get_specific_category()
    return render_template('categories.html', output=output)


# add review to movie
@routes_bp.route('/review/<int:entries_id>', methods=['POST'])
def review(entries_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    query = request.form.get('query')
    print("review query: ", query)
    print(api_review(user_id, entries_id, query))
    return render_template('movie_details.html', )


@routes_bp.route('/rate/<int:entries_id>')  # rate movies
def rate(entries_id):
    return
