from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import mysql.connector


# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(movie_list):
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
    SELECT entries.entries_id, entries.title, entries.overview, people.name
    FROM entries, role, people
    WHERE entries.entries_id = role.entries_id_fk
        AND role.people_id_fk = people.people_id
    """
    cursor.execute(metadata_query)
    results = cursor.fetchall()

    titles = []
    metadata = {}
    director_weight = 3

    for entry_id, title, overview, actor_name in results:
        if title not in metadata:
            # Initialisation des données pour un nouveau film
            metadata[title] = {'overview': overview, 'actors': []}
            titles.append(title)
        # Ajout de chaque acteur à la liste des acteurs pour ce film
        metadata[title]['actors'].append(actor_name)

    # Création des métadonnées finales après agrégation
    final_metadata = []
    for title in titles:
        actors_string = ' '.join(metadata[title]['actors']) * director_weight
        overview = (metadata[title]['overview'] + ' ')
        combined_text = overview + ' ' + actors_string
        final_metadata.append(combined_text)
    
    # Initialize the TF-IDF Vectorizer
    tf_idf = TfidfVectorizer(stop_words='english')

    # Fit and transform the overviews to TF-IDF
    tfidf_matrix = tf_idf.fit_transform(final_metadata)

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
    top_indices = cosine_similarities.argsort()[-11:][::-1]
    # Exclude self-match if any of the input movies are also in the fetched results
    top_indices = [i for i in top_indices if titles[i] not in movie_list][:10]

    # Print or return the titles of the top recommendations
    recommended_titles = [titles[i] for i in top_indices]
    for title in recommended_titles:
        print(title)

    cursor.close()
    connection.close()

    return recommended_titles
