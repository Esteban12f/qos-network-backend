from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MeasurementCreate(BaseModel):
    session_id: str = Field(
        ...,
        min_length=3,
        description="Identificador único de la sesión del usuario"
    )

    latency_ms: float = Field(
        ...,
        ge=0,
        description="Latencia promedio medida desde el navegador en milisegundos"
    )

    jitter_ms: float = Field(
        ...,
        ge=0,
        description="Variación de latencia medida desde el navegador"
    )

    download_mbps: float = Field(
        ...,
        ge=0,
        description="Velocidad aproximada de descarga en Mbps"
    )

    upload_mbps: Optional[float] = Field(
        default=None,
        ge=0,
        description="Velocidad aproximada de subida en Mbps"
    )

    failed_requests: int = Field(
        default=0,
        ge=0,
        description="Cantidad de solicitudes fallidas o con timeout"
    )

    total_requests: int = Field(
        ...,
        gt=0,
        description="Cantidad total de solicitudes realizadas durante la prueba"
    )

    measurement_duration_s: float = Field(
        ...,
        gt=0,
        description="Duración total de la prueba en segundos"
    )

    client_timestamp: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora generada por el frontend"
    )

    device_type: Optional[str] = Field(
        default=None,
        description="Tipo de dispositivo: mobile, desktop, tablet, etc."
    )

    network_type: Optional[str] = Field(
        default=None,
        description="Tipo de red reportada por el navegador si está disponible"
    )

    @field_validator("failed_requests")
    @classmethod
    def failed_requests_must_not_exceed_total(cls, value, info):
        total_requests = info.data.get("total_requests")

        if total_requests is not None and value > total_requests:
            raise ValueError("failed_requests no puede ser mayor que total_requests")

        return value


class MeasurementResponse(BaseModel):
    session_id: str
    latency_ms: float
    jitter_ms: float
    download_mbps: float
    upload_mbps: Optional[float]
    failed_requests: int
    total_requests: int
    packet_loss_pct: float
    measurement_duration_s: float
    server_timestamp: datetime