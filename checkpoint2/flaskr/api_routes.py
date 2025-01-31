from flask import (jsonify,
                   request, session, Blueprint, url_for, redirect)
from db import get_db_connection
import auth
from algo import get_recommendations, get_recommendation_watchlist
import json
import datetime

api_bp = Blueprint('api_routes', __name__)


@api_bp.route("/api", methods=['GET'])
def getIndex():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    mysql_query = """ SELECT * FROM entries ORDER BY RAND() LIMIT 1000;"""
    cursor.execute(mysql_query)
    output = cursor.fetchall()

    cursor.close()
    connection.close()

    # return jsonify(output)
    return output


@api_bp.route("/api/movies/<int:entries_id>", methods=['GET'])
def getMovieDetails(entries_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            e.entries_id,
            e.date,
            e.title,
            e.length,
            e.universe_id_fk,
            e.overview,
            GROUP_CONCAT(c.category_name SEPARATOR ', ') AS categories
        FROM entries e
        LEFT JOIN entries_category ec ON ec.entries_id_fk = e.entries_id
        LEFT JOIN category c ON c.category_id = ec.category_id_fk
        WHERE e.entries_id = %s
        GROUP BY e.entries_id;
        """
    cursor.execute(query, (entries_id,))
    movie = cursor.fetchone()

    # Query to fetch reviews for the movie
    reviews_query = """
        SELECT
            review.body,
            review.creation_date,
            review.rating,
            user.pseudo
        FROM review, user
        WHERE entries_id_fk = %s and review.user_id_fk = user.user_id;
        """
    cursor.execute(reviews_query, (entries_id,))
    reviews = cursor.fetchall()
    print(reviews)

    cursor.close()
    connection.close()

    return movie, reviews


@api_bp.route('/api/similarmovie/<int:entries_id>/', methods=['GET'])
def getSimilarMovieDetails(titles):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # similar_movies_details = []
    title_placeholders = ','.join(['%s'] * len(titles))

    for title in titles:
        cursor.execute(
            f"""
            SELECT DISTINCT entries.entries_id, entries.date, entries.title,
            entries.length, entries.overview FROM entries
            WHERE entries.title IN ({title_placeholders});
            """, titles)
        movie = cursor.fetchall()
        # cursor.fetchall()  # cleans the cursor of unread results
        # similar_movies_details.append(movie)

    cursor.close()
    connection.close()

    return movie


@api_bp.route("/api/recommendation", methods=['GET'])
def getRecommendations():
    title = []
    title.append(request.headers.get('args'))
    recommendations = get_recommendations(title)
    return recommendations


@api_bp.route("/api/watchlist_recommendation", methods=['GET'])
def getWatchlistRecommendation():
    good_titles = request.args.get('good_titles', '').split(',')
    bad_titles = request.args.get('bad_titles', '').split(',')

    print(good_titles)
    print(bad_titles)

    recommendations = get_recommendation_watchlist(good_titles, bad_titles)
    print(recommendations)

    return jsonify(recommendations)


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


@api_bp.route('/api/watchlist', methods=['GET'])
def view_watchlist():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # Check if user is logged in
    if 'user_id' not in session:
        cursor.close()
        connection.close()
        return redirect(url_for(auth.login))

    user_id = session['user_id']

    cursor.execute(
        "SELECT * FROM entries INNER JOIN watchlist ON entries.entries_id = watchlist.entries_id_fk WHERE watchlist.user_id_fk = %s", (
            user_id,)
    )
    watchlist = cursor.fetchall()
    cursor.close()
    connection.close()

    return watchlist


@api_bp.route('/api/add/<int:entries_id>', methods=['POST'])
def api_add_to_watchlist(user_id, entries_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM watchlist WHERE user_id_fk = %s AND entries_id_fk = %s",
            (user_id, entries_id))
        existing_entry = cursor.fetchone()

        if existing_entry:
            # If the movie already exists in the watchlist, return an error response
            return jsonify({'success': False, 'message': 'Movie already exists in watchlist'}), 400

        cursor.execute(
            "INSERT INTO watchlist (user_id_fk, entries_id_fk) VALUES (%s, %s)",
            (user_id, entries_id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'success': True, 'message': 'Movie added to watchlist'}), 200
    except Exception as e:
        # Handle the error and return false
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/remove/<int:entries_id>', methods=['POST'])
def api_remove_from_watchlist(user_id, entries_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "DELETE FROM watchlist WHERE user_id_fk = %s AND entries_id_fk = %s;",
            (user_id, entries_id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'success': True, 'message': 'Movie removed from watchlist'}), 200
    except Exception as e:
        # Handle the error and return false
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/api/category', methods=['GET'])
def getCategories():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT DISTINCT category_name FROM category;")
    categories = cursor.fetchall()
    cursor.close()
    connection.close()

    return categories


@api_bp.route('/api/category/{{ category }}', methods=['GET'])
def get_specific_category(category):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
                    SELECT entries.*
                    FROM entries
                    JOIN entries_category ON entries.entries_id = entries_category.entries_id_fk
                    JOIN category ON entries_category.category_id_fk = category.category_id
                    WHERE category.category_name = %s;
                    """, (category,))
    categories = cursor.fetchall()
    cursor.close()
    connection.close()

    return categories


@api_bp.route('/api/review/<int:entries_id>', methods=['POST'])
def api_review(user_id, entries_id, comment, rating=-1):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    current_timestamp = datetime.datetime.now()

    query = """
        INSERT INTO review (entries_id_fk, body, user_id_fk, rating, creation_date)
        VALUES (%s, %s, %s, %s, %s);
        """
    values = (entries_id, comment, user_id, rating, current_timestamp)

    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'success': True, 'message': 'Review added to movie'}), 200
