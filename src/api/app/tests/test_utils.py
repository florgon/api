"""
    Tests utils API methods.
"""


def test_read_utils_get_server_time(client):  # pylint: disable=redefined-outer-name
    """Tests that server responds with time for utils get server time method."""
    response = client.get("/v1/utils/status/")
    assert response.status_code == 200

    json = response.json()
    assert "success" in json
    assert "v" in json
    assert "server_time" in json["success"]
