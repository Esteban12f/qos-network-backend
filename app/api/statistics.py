from fastapi import APIRouter, HTTPException

from app.schemas.statistics import StatisticsResponse
from app.services.statistics_service import statistics_service

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"]
)


@router.get("/{session_id}", response_model=StatisticsResponse)
def get_statistics(session_id: str):
    """
    Calcula estadísticas usando las mediciones reales enviadas por Angular.
    """
    statistics_result = statistics_service.get_statistics(session_id)

    if statistics_result is None:
        raise HTTPException(
            status_code=404,
            detail="No existen suficientes mediciones para calcular estadísticas."
        )

    return statistics_result