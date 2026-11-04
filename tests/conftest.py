import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app


@pytest.fixture
def client():
    test_settings = Settings(app_name="examate-rag", environment="test")

    app.dependency_overrides[get_settings] = lambda: test_settings

    try:
        with TestClient(app) as c:
            c.settings = test_settings
            yield c
    finally:
        app.dependency_overrides.clear()
