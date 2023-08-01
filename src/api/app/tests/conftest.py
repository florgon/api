import pytest
from fastapi.testclient import TestClient
from app.config import get_settings
from app.app import create_application


def pytest_configure(*_):
    if not get_settings().is_development:
        raise Exception("Tests should not be executed on production environment!")


@pytest.fixture(scope="session")
def client():
    """Web server application fixture to have app initialized."""
    with TestClient(create_application()) as c:
        yield c
