from db import get_db_connection
# nothing here


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_search(client):
    response = client.get("/search?query=StarWars")
    assert response.status_code == 200


def test_movie(client):
    response = client.get("/movie/11")
    assert response.status_code == 200

    response2 = client.get("/movie/0")
    assert response2.status_code == 404
    assert b"Movie not found" in response2.data


def test_advanced_search(client):
    query_param = "orange cat hate mondays"
    response = client.get(f"/advancedsearch?query={query_param}")
    assert response.status_code == 200


def test_review(client):
    client.get("/logout")
    response = client.post(
        "/review/11", data={"query": "Test: best movie ever"})
    assert response.status_code == 302


def test_login(client):
    login_resp = client.get("login")
    assert login_resp.status_code == 200
    response = client.post(
        "/login", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 302


def test_watchlist_authenticated(client):
    # Log in a user (assuming you have a user with id=1)
    client.post(
        "/login", data={"username": "testuser", "password": "testpassword"})
    # Make a request to the /watchlist route
    response = client.get("/watchlist")

    # Check that the response status code is 200
    assert response.status_code == 200


def test_add(client):
    client.get("/logout")
    response = client.post("/add/3")
    assert response.status_code == 302


def test_db(client):
    with client.application.app_context():
        db = get_db_connection()
        assert db is not None
