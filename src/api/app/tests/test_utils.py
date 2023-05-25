"""
    Tests utils API methods.
"""

import pytest
from app.app import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Web server application fixture to have app initialized."""
    with TestClient(app) as c:
        yield c


def test_read_utils_get_server_time(client):  # pylint: disable=redefined-outer-name
    """Tests that server responds with time for utils get server time method."""
    response = client.get("/utils.getServerTime")
    assert response.status_code == 200

    json = response.json()
    assert "success" in json
    assert "v" in json
    assert "server_time" in json["success"]
