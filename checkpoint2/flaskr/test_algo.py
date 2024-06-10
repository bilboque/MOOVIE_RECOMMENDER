def test_db_connection(client):
    response = client.db_connect()
    assert response is not None


def test_get_metadata(client):
    response, response2 = client.fetch_metadata()
    assert response is not None
    assert response2 is not None
