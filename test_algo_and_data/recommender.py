from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import mysql.connector
import functools

import mplcursors
import matplotlib
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.lines as mlines
from sklearn.metrics.pairwise import euclidean_distances
import itertools
import numpy as np


def plot_tsne_with_genres(tfidf_matrix, titles, meta_data):
    titles = titles[:1000]
    tfidf_matrix = tfidf_matrix[:1000]
    # Initialize t-SNE
    tsne = TSNE(n_components=3, verbose=1, perplexity=40)
    tsne_results = tsne.fit_transform(tfidf_matrix.toarray())

    # Setting up color map
    colors = {'Science Fiction': 'blue', 'Romance': 'red',
              'Both': 'green', 'Other': 'grey'}

    # Plotting
    fig = plt.figure(figsize=(16, 10))
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

    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(tsne_results[:, 0],
                         tsne_results[:, 1],
                         tsne_results[:, 2],
                         color=scatter_colors, alpha=0.5)
    cursor = mplcursors.cursor(scatter, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        titles[sel.target.index]))

    # Create legend dynamically from the colors dict
    legend_elements = [mlines.Line2D([0], [0], marker='o',
                                     color='w',
                                     markerfacecolor=color,
                                     markersize=10,
                                     label=genre)
                       for genre, color in colors.items()]

    ax.legend(handles=legend_elements, loc='upper right')
    ax.set_title('t-SNE visualization of Movie Data by Genre')
    ax.set_xlabel('t-SNE feature 1')
    ax.set_ylabel('t-SNE feature 2')
    ax.set_zlabel('t-SNE feature 3')
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
    return tf_idf, tfidf_matrix, titles, metadata


# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(movie_list):
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
    top_indices = [i for i in top_indices if titles[i] not in movie_list][:10]

    recommended_titles = [titles[i] for i in top_indices]

    return recommended_titles


def get_top_keywords(film, top_n):
    tf_idf, tfidf_matrix, titles, metadata = get_tfidf_matrix()

    if film not in titles:
        return f"The film '{film}' is not in the list of titles."

    film_idx = titles.index(film)
    feature_names = tf_idf.get_feature_names_out()
    tfidf_scores = tfidf_matrix[film_idx].toarray().flatten()
    top_indices = np.argsort(tfidf_scores)[::-1][:top_n]
    top_keywords = [feature_names[i]
                    for i in top_indices if tfidf_scores[i] > 0]

    return top_keywords


def get_watchlist_keywords(watchlist):
    all_keywords = []
    for film in watchlist:
        all_keywords.extend(get_top_keywords(film, 2))

    return all_keywords
