from fastapi import APIRouter, HTTPException

from app.schemas.queue import QueueRealtimeResponse
from app.services.queue_service import queue_service

router = APIRouter(
    prefix="/queue",
    tags=["Queue"]
)


@router.get("/realtime/{session_id}", response_model=QueueRealtimeResponse)
def get_realtime_queue(session_id: str):
    """
    Calcula métricas de teoría de colas M/M/1.

    Calcula:
    - λ
    - μ
    - ρ
    - L
    - Lq
    - W
    - Wq
    - probabilidad estimada de congestión
    """
    queue_result = queue_service.get_realtime_queue_metrics(session_id)

    if queue_result is None:
        raise HTTPException(
            status_code=404,
            detail="No existen datos suficientes para calcular el modelo de colas."
        )

    return queue_result