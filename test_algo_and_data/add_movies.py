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

# Wrapper requests les 10 000 films les plus populaires
# on peut aller jusqu'a 20 000 films normalement
# si range(1, n) insere 20*n films sans les films adultes
for i in range(1, 500):
    resp = movies.top_rated(page=i)
    if 'results' in resp:
        for film in resp['results']:
            add_movie(cursor, film)
    else:
        print(f"La page {i} n'a pas pu être chargée ou est vide.")


# commit les changements
connection.commit()

# Fermeture du curseur et de la connexion à la DB
cursor.close()
connection.close()
