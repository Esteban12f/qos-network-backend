from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name:    str = "QoS Network Monitor API"
    app_version: str = "1.0.0"
    environment: str = "development"

    frontend_origins: str = (
        "http://localhost:4200,http://127.0.0.1:4200,"
        "https://qos-network-dashboard.web.app"
    )
    database_url:     str = "postgresql://user:password@localhost:5432/qos_db"

    firebase_project_id: str = "qos-network-dashboard"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.frontend_origins.split(",") if o.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()