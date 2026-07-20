from fastapi import APIRouter, Depends, HTTPException

from app.core.firebase_auth import CurrentUser, get_current_user
from app.schemas.measurement import MeasurementCreate, MeasurementResponse
from app.services.measurement_service import measurement_service

router = APIRouter(
    prefix="/measurements",
    tags=["Measurements"]
)


@router.post("/ingest", response_model=MeasurementResponse)
def ingest_measurement(
    measurement: MeasurementCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
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
        return measurement_service.ingest_measurement(current_user.uid, measurement)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.delete("/{session_id}")
def clear_measurements(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Limpia las mediciones de una sesión.
    Útil para reiniciar una prueba desde el frontend.
    """
    deleted = measurement_service.clear_session(current_user.uid, session_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="No existen mediciones para la sesión indicada."
        )

    return {
        "status": "deleted",
        "session_id": session_id
    }