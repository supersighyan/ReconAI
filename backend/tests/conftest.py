import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://reconai:reconai@127.0.0.1:5432/reconai",
)

from app.core.config import get_settings
from app.core.database import get_engine
from app.main import create_app

get_settings.cache_clear()
get_engine.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())
