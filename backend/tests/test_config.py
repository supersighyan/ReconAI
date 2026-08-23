from pytest import MonkeyPatch

from app.core.config import Settings, get_settings


def test_configuration_loads_from_environment(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://example:example@localhost:5432/reconai",
    )
    monkeypatch.setenv("APP_NAME", "ReconAI-Test")
    get_settings.cache_clear()

    settings = Settings()

    assert settings.app_name == "ReconAI-Test"
    assert settings.database_url.endswith("/reconai")
    assert "example" in settings.database_url
