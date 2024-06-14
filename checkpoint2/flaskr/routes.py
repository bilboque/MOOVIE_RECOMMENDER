from flask import (render_template,
                   request, session, Blueprint, url_for, redirect,
                   jsonify)

from api_routes import (getIndex, searchEntry,
                        getMovieDetails, view_watchlist, api_add_to_watchlist,
                        api_remove_from_watchlist, getCategories,
                        get_specific_category, getSimilarMovieDetails,
                        getRecommendations, api_review)
from algo import get_recommendations, average_rating

routes_bp = Blueprint('routes', __name__)


@routes_bp.route("/", methods=['GET'])
def index():
    output = getIndex()
    return render_template('app.html', output=output)


@routes_bp.route("/about")
def about():
    return "<h3>This is an IMDb project; codename DBMi</h3>"


@routes_bp.route("/search", methods=['GET'])  # perform a normal search
def search():
    query = request.args.get('query')
    search = searchEntry(query)
    return render_template('app.html', output=search)


# perform an advanced search
@routes_bp.route("/advancedsearch", methods=['GET'])
def advanced_search():
    query = request.args.get('query')
    if query:
        advance = get_recommendations([query])
        result = getSimilarMovieDetails(advance)
    else:
        print("nothing found in advanced search")
        result = []
    return render_template('advanced.html', output=result)


# display further information on a movie
@routes_bp.route('/movie/<int:entries_id>', methods=['GET'])
def movieDetails(entries_id):
    details, reviews = getMovieDetails(entries_id)

    # Ensure `details` is not None
    if not details:
        return "Movie not found", 404

    similar = get_recommendations([details['title']])
    similarMovieDetails = getSimilarMovieDetails(similar)
    ratings = [review['rating'] for review in reviews]

    return render_template('movie_details.html', details=details,
                           similar_movies=similarMovieDetails,
                           reviews=reviews,
                           average_rating=average_rating(ratings))


@routes_bp.route('/watchlist', methods=['GET'])  # display watchlist
def viewWatchlist():
    watchlist = view_watchlist()
    movies = []
    for movie in watchlist:
        movies.append(movie['title'])

    return render_template('watchlist.html', output=watchlist)


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
    rating = request.form.get('rating')
    print("review query: ", query)
<<<<<<< HEAD
    api_review(user_id, entries_id, query)
    # -> go to moviedetails function and use the render_template there
    return redirect(url_for('routes_bp.movieDetails', entries_id=entries_id))
=======
    api_review(user_id, entries_id, query, rating)

    return redirect(url_for('routes.movieDetails', entries_id=entries_id))


@routes_bp.route('/rate/<int:entries_id>')  # rate movies
def rate(entries_id):
    return
>>>>>>> 4c88ccdbc5379ae1565bf6faa9558e5d63e5eda8
