from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import euclidean_distances
import mysql.connector
from flask import current_app
import functools


def read_db_password():
    try:
        with open('password.txt', 'r') as file:
            password = file.readline().strip()  # Assuming password is stored in a single line
        return password
    except FileNotFoundError:
        return None


def db_connect():
    # create db connection
    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=read_db_password(),
        database="DBMi"  # db name to access
    )

    return connection.cursor(), connection


cache = current_app.extensions['cache']  # Access the cache instance


@functools.lru_cache(maxsize=1)
def fetch_metadata():
    cursor, connection = db_connect()

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
    return tf_idf, tfidf_matrix, titles


# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(movie_list):
    tf_idf, tfidf_matrix, titles = get_tfidf_matrix()

    # Concatenate the overviews of the input movies
    input_metadata = []
    for title in movie_list:
        if title in titles:
            input_metadata.append(titles.index(title))
        else:
            input_metadata.append(title)

    input_text = ' '.join(input_metadata)

    # Transform the concatenated input movie metadata
    input_tfidf = tf_idf.transform([input_text])

    # Compute cosine similarities between input movies and database entries
    dist = euclidean_distances(input_tfidf, tfidf_matrix).flatten()

    # Get top 10 similar movies
    top_indices = dist.argsort()[::]
    top_indices = [i for i in top_indices if titles[i] not in movie_list][:10]

    recommended_titles = [titles[i] for i in top_indices]

    return recommended_titles
