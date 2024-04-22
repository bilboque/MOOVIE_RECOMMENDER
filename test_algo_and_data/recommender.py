from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import mysql.connector


# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(movie):
    # connection to DB
    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="root1234",
        database="IMDb"
    )

    cursor = connection.cursor()

    # Load-data
    metadata_query = """
    SELECT entries.entries_id, entries.title, entries.overview
    FROM entries
    """
    cursor.execute(metadata_query)
    results = cursor.fetchall()

    titles = []
    overviews = []

    # Check if overviews are not None and then append to list
    for entry_id, title, overview in results:
        if overview:  # only consider entries with an overview
            titles.append(title)
            overviews.append(overview)

    # Initialize the TF-IDF Vectorizer
    tf_idf = TfidfVectorizer(stop_words='english')

    # Fit and transform the overviews to TF-IDF
    tfidf_matrix = tf_idf.fit_transform(overviews)

    # Display some results or further process tfidf_matrix
    print("TF-IDF features shape:", tfidf_matrix.shape)

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    idx = titles.index(movie)
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]

    movie_indices = [i[0] for i in sim_scores]

    for i in movie_indices:
        print(titles[i])

    cursor.close()
    connection.close()
    return
