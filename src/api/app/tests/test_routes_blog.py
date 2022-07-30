import pytest

from fastapi.testclient import TestClient

from app.app import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_read_blog_get(client):
    response = client.get("/blog.get")
    assert response.status_code == 200

    json = response.json()
    assert "success" in json
    assert "v" in json
    assert "posts" in json["success"]

    response = client.get("/blog.get?post_id=1")
    assert response.status_code == 200

    json = response.json()
    assert "success" in json
    assert "v" in json
    assert "post" in json["success"]