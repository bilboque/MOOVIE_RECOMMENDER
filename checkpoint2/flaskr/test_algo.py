import unittest
from algo import fetch_metadata, get_tfidf_matrix, get_recommendations
from db import get_db_connection


class TestAlgo(unittest.TestCase):
    def test_db(self):
        connection = get_db_connection()
        cursor = connection.cursor()
        self.assertIsNotNone(cursor, "Db Cursor is None")
        self.assertIsNotNone(connection, "Db Connection is None")

    def test_title_numbers(self):
        connection = get_db_connection()
        cursor = connection.cursor()
        titles, _ = fetch_metadata()

        # Fetch the number of movies directly from the database
        cursor.execute('SELECT COUNT(*) FROM entries')
        db_count = cursor.fetchone()[0]

        # Compare the number of movies in the database with the length of the list
        self.assertEqual(db_count, len(
            titles), "Number of movies in DB does not match length of titles list")

    def test_metadata(self):
        connection = get_db_connection()
        cursor = connection.cursor()
        titles, metadata = fetch_metadata()

        entrie = "'Star Wars'"
        # Fetch the number of movies directly from the database
        cursor.execute(f"SELECT overview FROM entries WHERE title = {entrie}")
        overview = cursor.fetchone()[0]

        # Compare the number of movies in the database with the length of the list
        self.assertEqual(metadata['Star Wars']['overview'],
                         overview,
                         "Number of movies in DB does not match length of titles list")

    def test_tfidf_matrix(self):
        _, tfidf_matrix, titles, _ = get_tfidf_matrix()

        self.assertEqual(tfidf_matrix.shape[0], len(
            titles), "Number of rows in TF-IDF matrix does not match number of titles")

    def test_get_recommendation(self):
        movies = get_recommendations(['Star Wars'])

        self.assertNotIn('Star Wars', movies,
                         'You should not get the same movie back')
        self.assertEqual(10, len(movies), 'You should get 10 movies back')

    def test_recommendation_QA(self):
        movies = get_recommendations(
            ['a movie about a lazy cat who eats lasagna'])
        self.assertIn('Garfield', movies, 'Bad recommendation Quality')

        movies = get_recommendations(
            ['a story about a superhero with spider-like abilities'])
        self.assertIn('Spider-Man', movies, 'Bad recommendation Quality')

        movies = get_recommendations(
            ['a panda who become a kung-fu master with a dad goose'])
        self.assertIn('Kung Fu Panda', movies,
                      'Bad recommendation Quality')

        movies = get_recommendations(
            ['flash mcqueen'])
        self.assertIn('Cars', movies,
                      'Bad recommendation Quality')


if __name__ == '__main__':
    unittest.main()
