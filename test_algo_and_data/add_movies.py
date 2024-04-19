import tmdbsimple as tmdb
import mysql.connector  # this works


# ajoute un film
def add_movie(cursor, movie: dict):
    # Vérifier si le film existe déjà
    cursor.execute("SELECT entries_id FROM entries WHERE entries_id = %s", (movie['id'],))
    if cursor.fetchone():
        print(f"Le film avec l'ID {movie['id']} existe déjà.")
        return

    if not movie['adult']:
        try:
            # Requête SQL pour insérer un film
            insert_query = """
            INSERT INTO entries (entries_id, date, title, length, overview, universe_id_fk)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            # Les valeurs à insérer
            movie_data = (
                movie['id'],
                movie['release_date'],
                movie['title'],
                None,
                movie['overview'],
                None
            )

            # Exécution de la requête SQL
            cursor.execute(insert_query, movie_data)

            print(f"Ajout du film '{movie['title']}'")
        except mysql.connector.Error as e:
            print("Erreur lors de l'insertion du film:", e)


# Ajoute un genre a la db
def add_genre(cursor, genre: dict):
    # Vérifier si le genre existe déjà
    cursor.execute("SELECT category_id FROM category WHERE category_id = %s", (genre['id'],))
    if cursor.fetchone():
        print(f"Le genre avec l'ID {genre['id']} existe déjà.")
        return

    try:
        # Requête SQL pour insérer un genre
        insert_query = """
        INSERT INTO category (category_id, category_name)
        VALUES (%s, %s)
        """
        # Exécution de la requête SQL avec les données du genre
        cursor.execute(insert_query, (genre['id'], genre['name']))

        print(f"Ajout du genre '{genre['name']}' avec l'ID {genre['id']}")
    except mysql.connector.Error as e:
        print(f"Erreur lors de l'ajout du genre '{genre['name']}':", e)


# Update movies infos
# cette fonction update les infos suivantes
# -> longeur, univers fk
# cette fonction ajoute des elements dans la table entrie categorie
# cette fonction ajoute aussi les univers des films
def update_all_movies_infos():
    # Récupérer tous les IDs des films de la base de données
    cursor.execute("SELECT entries_id FROM entries")
    movie_ids = cursor.fetchall()
    universe_fk = None

    for (movie_id,) in movie_ids:
        # Récupérer les détails du film depuis TMDB
        try:
            movies = tmdb.Movies(movie_id)
            resp = movies.info()
        except Exception as e:
            print(f"Erreur lors de la récupération des détails pour le film ID {movie_id}: {e}")
            continue

        # Ajouter les genres dans la table entries_category
        for genre in resp.get('genres', []):
            insert_genre_query = """
            INSERT INTO entries_category (entries_id_fk, category_id_fk)
            VALUES (%s, %s)
            """
            cursor.execute(insert_genre_query, (movie_id, genre['id']))
            print(f"Ajout de la relation '{genre['name']}' avec le film id {movie_id}")

        # Creation de l'univers si besoin
        collection = resp['belongs_to_collection']
        if collection:
            # Vérifier si la collection existe déjà dans la table universe
            cursor.execute("SELECT universe_id FROM universe WHERE universe_id = %s", (collection['id'],))
            if not cursor.fetchone():
                # Si elle n'existe pas, insérez-la
                insert_universe_query = """
                INSERT INTO universe (universe_id, name, description)
                VALUES (%s, %s, NULL)
                """
                cursor.execute(insert_universe_query, (collection['id'], collection['name']))
                universe_fk = collection['id']
                print(f"Ajout de la collection '{collection['name']}' avec le film id {movie_id}")
            else:
                universe_fk = None

        # Mise à jour des informations de longueur et univers fk dans la table entries
        runtime = resp['runtime']  # runtime est en minutes apriori
        update_query = """
        UPDATE entries
        SET length = %s, universe_id_fk = %s
        WHERE entries_id = %s
        """
        cursor.execute(update_query, (f"{runtime//60:02}:{runtime%60:02}:00", universe_fk, movie_id))
        print(f"Update movie (id = {movie_id})")

    print("Update process completed.")


# connection to DB
connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="root1234",
    database="IMDb"
)

cursor = connection.cursor()


# connection a tmdb api
tmdb.API_KEY = '12c3bacebdccca9238e8944139bb557a'
tmdb.REQUESTS_TIMEOUT = 5

# Base class
movies = tmdb.Movies()

# # Wrapper requests les 10 000 films les plus populaires
# # on peut aller jusqu'a 20 000 films normalement
# # si range(1, n) insere 20*n films sans les films adultes
# for i in range(1, 500):
#     resp = movies.top_rated(page=i)
#     if 'results' in resp:
#         for film in resp['results']:
#             add_movie(cursor, film)
#     else:
#         print(f"La page {i} n'a pas pu être chargée ou est vide.")


# Wrapper request pour obtenir les genres
genres = tmdb.Genres()
resp = genres.movie_list()

for genre in resp['genres']:
    add_genre(cursor, genre)

update_all_movies_infos()

# commit les changements
connection.commit()

# Fermeture du curseur et de la connexion à la DB
cursor.close()
connection.close()
