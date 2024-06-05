from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import euclidean_distances
import mysql.connector
<<<<<<< HEAD
# from temp_app import cache
=======
from flask import current_app
import functools
>>>>>>> e2d0c2f1773ca2bbd9e87ae4463e8deed03d13c3


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
        database="IMDb"  # db name to access
    )

    return connection.cursor(), connection


<<<<<<< HEAD
# cache = current_app.extensions['cache']  # Access the cache instance


# @cache.cached(key_prefix='tfidf_computation')
def get_tfidf(movie_list):
    # connection to DB
=======
@functools.lru_cache(maxsize=1)
def fetch_metadata():
>>>>>>> e2d0c2f1773ca2bbd9e87ae4463e8deed03d13c3
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
<<<<<<< HEAD
    # connection to DB
    cursor, connection = db_connect()

    print('movie list: ', movie_list)

    # Load-data movies and overview
    metadata_overiew = """
    SELECT entries.entries_id, entries.overview, entries.title
    FROM entries
    """
    cursor.execute(metadata_overiew)
    results = cursor.fetchall()

    titles = []
    metadata = {}

    for _, overview, title in results:
        metadata[title] = {'overview': overview,
                           'actors': [],
                           'genres': [],
                           'keywords': []}
        titles.append(title)

    # now fetch actors
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

    # now fetch genres
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

    # now fetch keywords
    metadata_genres = """
    select entries.title, keywords.keywords
    from entries, entries_keywords, keywords
    where entries.entries_id = entries_keywords.entries_id_fk
        and entries_keywords.keywords_id_fk = keywords.keywords_id
    """
    cursor.execute(metadata_genres)
    results = cursor.fetchall()

    for title, keyword in results:
        metadata[title]['keywords'].append(keyword)

    # default weights
    keywords_wght = 5
    genres_weight = 2
    actors_weight = 2
    overview_wght = 1

    if not set(movie_list).issubset(set(titles)):
        overview_wght = 4
        keywords_wght = 4

    # Création des métadonnées finales après agrégation
    final_metadata = []
    for title in titles:
        actors_string = (
            ' '.join(metadata[title]['actors']) + ' ') * actors_weight
        genres_string = (
            ' '.join(metadata[title]['genres']) + ' ') * genres_weight
        overview = ((metadata[title]['overview']) + ' ') * overview_wght
        keywords = (
            ' '.join(metadata[title]['keywords']) + ' ') * keywords_wght

        combined_text = overview + ' ' + actors_string + \
            ' ' + genres_string + ' ' + title + ' ' + keywords
        final_metadata.append(combined_text)

    # Initialize the TF-IDF Vectorizer
    tf_idf = TfidfVectorizer(stop_words='english', strip_accents='ascii')
    # tfidf_matrix = get_tfidf()

    # Fit and transform the overviews to TF-IDF
    tfidf_matrix = tf_idf.fit_transform(final_metadata)
    tfidf_matrix = get_tfidf(movie_list)
=======
    tf_idf, tfidf_matrix, titles = get_tfidf_matrix()
>>>>>>> e2d0c2f1773ca2bbd9e87ae4463e8deed03d13c3

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
