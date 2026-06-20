from expense_tracker import create_app


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_index(client):
    assert client.get("/").status_code == 200
