"""
    Tests blog API methods.
"""


import pytest
from fastapi.testclient import TestClient

from app.app import app


@pytest.fixture
def client():
    """Web server application fixture to have app initialized."""
    with TestClient(app) as c:
        yield c


def test_read_blog_get(client):  # pylint: disable=redefined-outer-name
    """Test blog public getter method."""
    response = client.get("/blog.get")
    assert response.status_code == 200

    json = response.json()
    assert "success" in json
    assert "v" in json
    assert "posts" in json["success"]

    response = client.get("/blog.get?post_id=1")
    json = response.json()
    assert "error" in json
    assert "v" in json
    assert "code" in json["error"]
    assert "status" in json["error"]
    error_status = json["error"]["status"]
    assert error_status == 404

    response = client.get("/blog.create")
    assert response.status_code != 200
