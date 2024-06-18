from db import get_db_connection
# nothing here


def test_home(client):  # checks that the home page is accessible
    response = client.get("/")
    assert response.status_code == 200


def test_search(client):  # ensures the search functionality works correctly
    response = client.get("/search?query=StarWars")
    assert response.status_code == 200


def test_movie(client):
    response = client.get("/movie/11")
    assert response.status_code == 200
    response2 = client.get("/movie/0")
    assert response2.status_code == 404
    assert b"Movie not found" in response2.data


def test_advanced_search(client):  # verifies the advanced search functionality
    query_param = "orange cat hate mondays"
    response = client.get(f"/advancedsearch?query={query_param}")
    assert response.status_code == 200


def test_db(client):
    with client.application.app_context():
        db = get_db_connection()
        assert db is not None
