from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class NetworkProfileConfirmRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=60,
        description="Nombre asignado por el usuario a la red",
    )

    network_type: str | None = Field(
        default=None,
        max_length=32,
        description="Tipo de conexión detectado por el navegador",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())

        if not cleaned:
            raise ValueError(
                "El nombre de la red no puede estar vacío."
            )

        return cleaned

    @field_validator("network_type")
    @classmethod
    def validate_network_type(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = value.strip().lower()

        return cleaned or None


class NetworkProfileSessionResponse(BaseModel):
    id: int
    name: str
    network_type: str | None

    session_id: str

    created_at: datetime
    updated_at: datetime

    session_started_at: datetime
    session_updated_at: datetime


class NetworkProfileListItem(BaseModel):
    id: int
    name: str
    network_type: str | None

    session_count: int
    last_used_at: datetime | None

    created_at: datetime
    updated_at: datetime


class NetworkProfilesListResponse(BaseModel):
    items: list[NetworkProfileListItem]
    total: int