"""
    Tests session API methods and overall auth process(?).
"""


import pytest
from app.app import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Web server application fixture to have app initialized."""
    with TestClient(app) as c:
        yield c


def test_read_session_signup_get_user_info(
    client,
):  # pylint: disable=redefined-outer-name
    """Complex check for signup, get user info, get profile info."""
    username = "tester"
    signup_response = client.get(
        "/_session._signup",
        params={
            "username": username,
            "email": "tester@example.com",
            "password": "password",
        },
    )

    json = signup_response.json()
    assert "v" in json
    if signup_response.status_code == 400:
        # If unable to authenticate,
        # check that blocked due to username/email taken.
        assert "error" in json
        assert "code" in json["error"]
        assert "status" in json["error"]
        error_status = json["error"]["status"]
        error_code = json["error"]["code"]
        assert error_status == 400

        # Check that error code, means that username or email already taken.
        assert error_code in (0, 1)
        return
    assert signup_response.status_code == 200
    assert "success" in json
    assert "session_token" in json["success"]

    session_token = json["success"]["session_token"]
    get_info_response = client.get(
        "/_session._getUserInfo", params={"session_token": session_token}
    )
    json = get_info_response.json()
    assert "v" in json
    assert "success" in json
    assert "user" in json["success"]
    assert "username" in json["success"]["user"]
    assert json["success"]["user"]["username"] == username

    get_profile_info_response = client.get(
        "/user.getProfileInfo", params={"username": username}
    )
    json = get_profile_info_response.json()
    assert "v" in json
    assert "success" in json
    assert "user" in json["success"]
    assert "username" in json["success"]["user"]
    assert json["success"]["user"]["username"] == username
