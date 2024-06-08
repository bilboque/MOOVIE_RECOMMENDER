def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_search(client):
    response = client.get("/search?query=StarWars")
    assert response.status_code == 200
