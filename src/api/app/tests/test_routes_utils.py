import pytest

from fastapi.testclient import TestClient

from app.app import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_read_utils_get_server_time(client):
    response = client.get("/utils.getServerTime")
    assert response.status_code == 200

    json = response.json() 
    assert "success" in json
    assert "v" in json
    assert "server_time" in json["success"]