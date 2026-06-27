from fastapi import APIRouter, HTTPException

from app.schemas.metrics import LiveMetricsResponse, MetricsHistoryResponse
from app.services.metrics_service import metrics_service

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"]
)


@router.get("/live/{session_id}", response_model=LiveMetricsResponse)
def get_live_metrics(session_id: str):
    """
    Devuelve la última medición registrada para una sesión.
    """
    metrics = metrics_service.get_live_metrics(session_id)

    if metrics is None:
        raise HTTPException(
            status_code=404,
            detail="No existen métricas para la sesión indicada."
        )

    return metrics


@router.get("/history/{session_id}", response_model=MetricsHistoryResponse)
def get_metrics_history(session_id: str):
    """
    Devuelve el historial de mediciones de una sesión.
    Este endpoint sirve para gráficas temporales en Angular.
    """
    history = metrics_service.get_metrics_history(session_id)

    if history.total_points == 0:
        raise HTTPException(
            status_code=404,
            detail="No existe historial para la sesión indicada."
        )

    return history