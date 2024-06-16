import functools
import numpy as np
from flask import current_app
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import euclidean_distances
import mysql.connector
from flask import Blueprint
from db import get_db_connection

algo_bp = Blueprint('algo', __name__)


@functools.lru_cache(maxsize=1)
def fetch_metadata():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Load movies and overviews
    metadata_overview = """
    SELECT entries.entries_id, entries.overview, entries.title
    FROM entries
    """
    cursor.execute(metadata_overview)
    results = cursor.fetchall()

    titles = []
    metadata = {}

    for _, overview, title in results:
        metadata[title] = {'overview': overview,
                           'actors': [], 'genres': [], 'keywords': []}
        titles.append(title)

    # Fetch actors
    metadata_actors = """
    SELECT title, people.name
    FROM entries, role, people
    WHERE entries.entries_id = role.entries_id_fk
        AND role.people_id_fk = people.people_id
    """
    cursor.execute(metadata_actors)
    results = cursor.fetchall()
    for title, name in results:
        metadata[title]['actors'].append(name)

    # Fetch genres
    metadata_genres = """
    SELECT title, category_name
    FROM entries, entries_category, category
    WHERE entries.entries_id = entries_category.entries_id_fk
      AND category.category_id = entries_category.category_id_fk
    """
    cursor.execute(metadata_genres)
    results = cursor.fetchall()
    for title, genre in results:
        metadata[title]['genres'].append(genre)

    # Fetch keywords
    metadata_keywords = """
    SELECT entries.title, keywords.keywords
    FROM entries, entries_keywords, keywords
    WHERE entries.entries_id = entries_keywords.entries_id_fk
        AND entries_keywords.keywords_id_fk = keywords.keywords_id
    """
    cursor.execute(metadata_keywords)
    results = cursor.fetchall()
    for title, keyword in results:
        metadata[title]['keywords'].append(keyword)

    cursor.close()
    connection.close()

    return titles, metadata


@functools.lru_cache(maxsize=1)
def get_tfidf_matrix():
    titles, metadata = fetch_metadata()

    # Assign weights
    keywords_weight = 5
    genres_weight = 2
    actors_weight = 2
    overview_weight = 1

    # Aggregate metadata
    final_metadata = []
    for title in titles:
        actors_string = (
            ' '.join(metadata[title]['actors']) + ' ') * actors_weight
        genres_string = (
            ' '.join(metadata[title]['genres']) + ' ') * genres_weight
        overview = (metadata[title]['overview'] + ' ') * overview_weight
        keywords = (
            ' '.join(metadata[title]['keywords']) + ' ') * keywords_weight

        combined_text = overview + ' ' + actors_string + \
            ' ' + genres_string + ' ' + title + ' ' + keywords
        final_metadata.append(combined_text)

    # Initialize the TF-IDF Vectorizer
    tf_idf = TfidfVectorizer(stop_words='english', strip_accents='ascii')

    # Fit and transform the aggregated metadata to TF-IDF
    tfidf_matrix = tf_idf.fit_transform(final_metadata)
    return tf_idf, tfidf_matrix, titles, metadata


# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(movie_list, excluded_movies=[]):
    tf_idf, tfidf_matrix, titles, metadata = get_tfidf_matrix()

    # Concatenate the overviews of the input movies
    input_metadata = []
    for title in movie_list:
        if title in titles:
            actors_string = (
                ' '.join(metadata[title]['actors']) + ' ') * 2
            genres_string = (
                ' '.join(metadata[title]['genres']) + ' ') * 2
            overview = (metadata[title]['overview'] + ' ') * 1
            keywords = (
                ' '.join(metadata[title]['keywords']) + ' ') * 5

            combined_text = overview + ' ' + actors_string + \
                ' ' + genres_string + ' ' + title + ' ' + keywords
            input_metadata.append(combined_text)

        else:
            input_metadata.append(title)

    input_text = ' '.join(input_metadata)

    # Transform the concatenated input movie metadata
    input_tfidf = tf_idf.transform([input_text])

    # Compute cosine similarities between input movies and database entries
    dist = euclidean_distances(input_tfidf, tfidf_matrix).flatten()

    # Get top 10 similar movies
    top_indices = dist.argsort()[::]
    top_indices = [i for i in top_indices if titles[i]
                   not in movie_list and titles[i] not in excluded_movies][:10]

    recommended_titles = [titles[i] for i in top_indices]

    return recommended_titles


def get_recommendation_watchlist(nice_movies, bad_movies):
    tf_idf, tfidf_matrix, titles, metadata = get_tfidf_matrix()

    feature_names = tf_idf.get_feature_names_out()

    nice_indices = [titles.index(movie)
                    for movie in nice_movies if movie in titles]
    bad_indices = [titles.index(movie)
                   for movie in bad_movies if movie in titles]

    nice_tfidf_sum = np.asarray(
        np.sum(tfidf_matrix[nice_indices], axis=0)).flatten()
    bad_tfidf_sum = np.asarray(
        np.sum(tfidf_matrix[bad_indices], axis=0)).flatten()

    summed_tfidf = nice_tfidf_sum - bad_tfidf_sum

    top_indices = np.argsort(summed_tfidf)[::-1][:10]
    top_keywords = [feature_names[i] for i in top_indices]
    print(top_keywords)

    return get_recommendations([' '.join(top_keywords)], excluded_movies=(bad_movies + nice_movies))


def average_rating(ratings):
    valid_ratings = [
        rating for rating in ratings if rating is not None and 1 <= rating <= 10]
    if not valid_ratings:
        return "N/A"
    return sum(valid_ratings) / len(valid_ratings)
