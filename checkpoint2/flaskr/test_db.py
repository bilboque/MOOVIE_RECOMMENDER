def test_db_connection(client):
    response = client.db_connect()
    assert response is not None
