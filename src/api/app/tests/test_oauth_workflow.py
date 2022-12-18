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


def test_read_oauth_implicit_signin_via_session(
    client,
):  # pylint: disable=redefined-outer-name
    """Does OAuth process with session sign-in and obtain access token (uses super user and super client)."""

    session_token = _signin_with_superuser(client)
    access_token = _obtain_access_token_via_implicit_oauth_flow(client, session_token)

    # Now we have both access and session tokens.
    user_get_info_response = client.get(
        "/user.getInfo",
        params={"access_token": access_token},
    )
    json = user_get_info_response.json()
    assert user_get_info_response.status_code == 200
    assert "success" in json

    # Logout after all stuff.
    _logout_request(client, session_token)


def test_read_oauth_authorization_code_signin_via_session(
    client,
):  # pylint: disable=redefined-outer-name
    """Does OAuth process with session sign-in and obtain access token (uses super user and super client)."""

    session_token = _signin_with_superuser(client)
    access_token = _obtain_access_token_from_oauth_code_grant(
        client,
        oauth_code=_obtain_oauth_code_via_authorization_oauth_flow(
            client, session_token
        ),
    )

    # TODO: Authorization code OAuth flow.
    # (Should use client secret that should be queried?)

    # Logout after all stuff.
    _logout_request(client, session_token)


def _signin_with_superuser(client) -> str:
    username = "admin"
    signin_response = client.get(
        "/_session._signin",
        params={
            "login": username,
            "password": "admin",
        },
    )
    json = signin_response.json()
    assert signin_response.status_code == 200
    assert "success" in json
    assert "session_token" in json["success"]
    session_token = json["success"]["session_token"]
    return session_token


def _obtain_oauth_code_via_authorization_oauth_flow(client, session_token: str):
    allow_client_response = client.get(
        "/_oauth._allowClient",
        params={
            "session_token": session_token,
            # Super client.
            "client_id": 1,
            "state": "",
            # Not used.
            "redirect_uri": "http://localhost",
            # We are may use star modifier as this is test environment.
            "scope": "*",
            # Authorization code oauth flow.
            "response_type": "code",
        },
    )
    assert allow_client_response.status_code == 200
    json = allow_client_response.json()
    assert "success" in json
    assert (
        "redirect_to" in json
    )  # Used in production scenarios with web-gateway (oauth screen)
    assert "code" in json["success"]
    oauth_code = json["success"]["oauth_code"]

    assert (
        oauth_code in json["success"]["redirect_to"]
    )  # Check that code is inside redirect to.
    return oauth_code


def _obtain_access_token_from_oauth_code_grant(client, oauth_code: str) -> str:
    return ""


def _obtain_access_token_via_implicit_oauth_flow(client, session_token: str):
    scope = "*"
    allow_client_response = client.get(
        "/_oauth._allowClient",
        params={
            "session_token": session_token,
            # Super client.
            "client_id": 1,
            "state": "",
            # Not used.
            "redirect_uri": "http://localhost",
            # We are may use star modifier as this is test environment.
            "scope": scope,
            # Implicit oauth flow.
            "response_type": "token",
        },
    )
    assert allow_client_response.status_code == 200
    json = allow_client_response.json()
    assert "success" in json
    assert (
        "redirect_to" in json
    )  # Used in production scenarios with web-gateway (oauth screen)
    assert "access_token" in json["success"]
    access_token = json["success"]["access_token"]
    if "*" in scope or "email" in scope:
        # Should be email field if we are requested.
        assert "email" in json["success"]
        assert "email" in json["success"]["redirect_to"]

    assert (
        access_token in json["success"]["redirect_to"]
    )  # Check that access token is inside redirect to.
    return access_token


def _logout_request(client, session_token: str) -> None:
    logout_response = client.get(
        "/_session._logout", params={"session_token": session_token, "revoke_all": True}
    )
    json = logout_response.json()
    assert logout_response.status_code == 200
    assert "success" in json
