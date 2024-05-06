from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import euclidean_distances
import mysql.connector


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


# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(movie_list):
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

    # Fit and transform the overviews to TF-IDF
    tfidf_matrix = tf_idf.fit_transform(final_metadata)

    # Concatenate the overviews of the input movies
    input_metadata = []
    for title in movie_list:
        if title in titles:
            input_metadata.append(final_metadata[titles.index(title)])
        else:
            input_metadata.append(title)

    input_text = ' '.join(input_metadata)  # Concatenate texts
    print('input text: ', input_text)

    # Transform the concatenated input movie metadata
    input_tfidf = tf_idf.transform([input_text])

    # Compute cosine similarities between input movies and database entries
    # dist = 1 - linear_kernel(input_tfidf, tfidf_matrix).flatten()
    # Calculate Euclidean distances
    dist = euclidean_distances(input_tfidf, tfidf_matrix).flatten()

    # Get top 10 similar movies
    top_indices = dist.argsort()[::]
    top_indices = [i for i in top_indices if titles[i] not in movie_list][:10]

    # Print or return the titles of the top recommendations
    recommended_titles = [titles[i] for i in top_indices]

    cursor.close()
    connection.close()

    print('output: ', recommended_titles)

    return recommended_titles
