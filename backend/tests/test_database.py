from sqlalchemy.engine import Engine

from app.core.database import get_engine


def test_database_engine_can_be_initialized() -> None:
    engine = get_engine()

    assert isinstance(engine, Engine)
    assert engine.url.drivername == "postgresql+psycopg"
    assert engine.dialect.name == "postgresql"
