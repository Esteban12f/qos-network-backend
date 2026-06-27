from fastapi import APIRouter, HTTPException

from app.schemas.measurement import MeasurementCreate, MeasurementResponse
from app.services.measurement_service import measurement_service

router = APIRouter(
    prefix="/measurements",
    tags=["Measurements"]
)


@router.post("/ingest", response_model=MeasurementResponse)
def ingest_measurement(measurement: MeasurementCreate):
    """
    Recibe una medición real generada desde Angular.

    El frontend mide:
    - latencia
    - jitter
    - throughput de descarga
    - throughput de subida, si existe
    - solicitudes fallidas
    - duración de la prueba
    """
    try:
        return measurement_service.ingest_measurement(measurement)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.delete("/{session_id}")
def clear_measurements(session_id: str):
    """
    Limpia las mediciones de una sesión.
    Útil para reiniciar una prueba desde el frontend.
    """
    deleted = measurement_service.clear_session(session_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="No existen mediciones para la sesión indicada."
        )

    return {
        "status": "deleted",
        "session_id": session_id
    }