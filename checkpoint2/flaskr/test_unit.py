from api_routes import getIndex, getMovieDetails


def test_getIndex(client):
    response = getIndex
    assert response is not None


def test_getMovieDetails():
    response = getMovieDetails(11)
    assert response is not None
