def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_search(client):
    response = client.get("/search?query=StarWars")
    assert response.status_code == 200


def test_movie(client):
    response = client.get("/movie/11")
    assert response.status_code == 200
