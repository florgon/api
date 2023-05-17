"""
    Tests session API methods and overall auth process(?).
"""


import pytest
from fastapi.testclient import TestClient
from app.database.bootstrap import SUPERUSER_USERNAME, SUPERUSER_PASSWORD
from app.app import app


@pytest.fixture
def client():
    """Web server application fixture to have app initialized."""
    with TestClient(app) as c:
        yield c


def test_read_session_signup_get_user_info(
    client,
):  # pylint: disable=redefined-outer-name
    """Complex check for signup, get user info, get profile info."""
    username = "pytestuser"
    signup_response = client.post(
        "/_session._signup",
        json={
            "username": username,
            "email": "pytest_user@example.com",
            "password": "password",
        },
    )

    json = signup_response.json()
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
    assert "success" in json
    assert "user" in json["success"]
    assert "username" in json["success"]["user"]
    assert json["success"]["user"]["username"] == username

    get_profile_info_response = client.get(
        "/user.getProfileInfo", params={"username": username}
    )
    json = get_profile_info_response.json()
    assert "success" in json
    assert "user" in json["success"]
    assert "username" in json["success"]["user"]
    assert json["success"]["user"]["username"] == username

    logout_response = client.get(
        "/_session._logout",
        params={"session_token": session_token, "revoke_all": False},
    )
    json = logout_response.json()
    assert logout_response.status_code == 200
    assert "success" in json


def test_read_session_superuser_signin(
    client,
):  # pylint: disable=redefined-outer-name
    """Check that super user is created and can be fetched."""
    signin_response = client.post(
        "/_session._signin",
        json={
            "login": SUPERUSER_USERNAME,
            "password": SUPERUSER_PASSWORD,
        },
    )

    json = signin_response.json()
    assert signin_response.status_code == 200
    assert "success" in json
    assert "session_token" in json["success"]

    session_token = json["success"]["session_token"]
    get_info_response = client.get(
        "/_session._getUserInfo", params={"session_token": session_token}
    )
    json = get_info_response.json()
    assert "success" in json
    assert "user" in json["success"]
    assert "username" in json["success"]["user"]
    assert json["success"]["user"]["username"] == SUPERUSER_USERNAME

    get_profile_info_response = client.get(
        "/user.getProfileInfo", params={"username": SUPERUSER_USERNAME}
    )
    json = get_profile_info_response.json()
    assert "success" in json
    assert "user" in json["success"]
    assert "username" in json["success"]["user"]
    assert json["success"]["user"]["username"] == SUPERUSER_USERNAME

    logout_response = client.get(
        "/_session._logout", params={"session_token": session_token, "revoke_all": True}
    )
    json = logout_response.json()
    assert logout_response.status_code == 200
    assert "success" in json
