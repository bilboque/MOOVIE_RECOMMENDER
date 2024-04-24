from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import mysql.connector

import mplcursors
import matplotlib
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE


def plot_tsne_with_genres(tfidf_matrix, titles, meta_data):
    # titles = titles[:1000]
    # tfidf_matrix = tfidf_matrix[:1000]
    # Initialize t-SNE
    tsne = TSNE(n_components=2, verbose=1, perplexity=40)
    tsne_results = tsne.fit_transform(tfidf_matrix.toarray())

    # Setting up color map
    colors = {'Science Fiction': 'blue', 'Romance': 'red',
              'Both': 'green', 'Other': 'grey'}

    # Plotting
    plt.figure(figsize=(16, 10))
    scatter_colors = []

    for i, title in enumerate(titles):
        genres = meta_data[title]['genres']
        if 'Science Fiction' in genres and 'Romance' in genres:
            cl = colors['Both']
        elif 'Science Fiction' in genres:
            cl = colors['Science Fiction']
        elif 'Romance' in genres:
            cl = colors['Romance']
        else:
            cl = colors['Other']

        scatter_colors.append(cl)

    scatter = plt.scatter(tsne_results[:, 0],
                          tsne_results[:, 1],
                          color=scatter_colors, alpha=0.5)
    cursor = mplcursors.cursor(scatter, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        titles[sel.target.index]))

    plt.title('t-SNE visualization of Movie Data by Genre')
    plt.xlabel('t-SNE feature 1')
    plt.ylabel('t-SNE feature 2')
    plt.show()


def db_connect():
    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="root1234",
        database="IMDb"
    )

    return connection.cursor(), connection


# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(movie_list):
    # connection to DB
    cursor, connection = db_connect()

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
        metadata[title] = {'overview': overview, 'actors': [], 'genres': []}
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

    genres_weight = 5
    actors_weight = 3
    overview_wght = 1

    # Création des métadonnées finales après agrégation
    final_metadata = []
    for title in titles:
        actors_string = (
            ' '.join(metadata[title]['actors']) + ' ') * actors_weight
        genres_string = (
            ' '.join(metadata[title]['genres']) + ' ') * genres_weight
        overview = ((metadata[title]['overview']) + ' ') * overview_wght
        combined_text = overview + ' ' + actors_string + ' ' + genres_string
        final_metadata.append(combined_text)

    # Initialize the TF-IDF Vectorizer
    tf_idf = TfidfVectorizer(stop_words='english')

    # Fit and transform the overviews to TF-IDF
    tfidf_matrix = tf_idf.fit_transform(final_metadata)
    plot_tsne_with_genres(tfidf_matrix, titles, metadata)

    # Concatenate the overviews of the input movies
    input_metadata = []
    for title in movie_list:
        input_metadata.append(final_metadata[titles.index(title)])
    input_text = ' '.join(input_metadata)  # Concatenate texts
    print(input_text)

    # Transform the concatenated input movie metadata
    input_tfidf = tf_idf.transform([input_text])

    # Compute cosine similarities between input movies and database entries
    cosine_similarities = linear_kernel(input_tfidf, tfidf_matrix).flatten()

    # Get top 10 similar movies
    top_indices = cosine_similarities.argsort()[::-1]
    top_indices = [i for i in top_indices if titles[i] not in movie_list][:10]

    # Print or return the titles of the top recommendations
    recommended_titles = [titles[i] for i in top_indices]

    cursor.close()
    connection.close()

    return recommended_titles
