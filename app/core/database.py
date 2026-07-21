from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.future_database_models import Base

_settings = get_settings()

engine = create_engine(
    _settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables() -> None:
    Base.metadata.create_all(bind=engine)

def ensure_user_id_column() -> None:
    """
    Migración idempotente para bases ya desplegadas: si la tabla measurements
    existe pero fue creada antes de que el modelo tuviera user_id, la agrega.
    Filas previas sin user_id quedan huérfanas (sin dueño) y se descartan.
    """
    inspector = inspect(engine)

    if "measurements" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("measurements")}

    if "user_id" in existing_columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE measurements ADD COLUMN user_id VARCHAR"))
        connection.execute(text("DELETE FROM measurements WHERE user_id IS NULL"))
        connection.execute(text("ALTER TABLE measurements ALTER COLUMN user_id SET NOT NULL"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_measurements_user_id ON measurements (user_id)"))