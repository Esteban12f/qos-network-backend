from fastapi import APIRouter, Depends, HTTPException

from app.core.firebase_auth import CurrentUser, get_current_user
from app.schemas.queue import QueueRealtimeResponse
from app.services.queue_service import queue_service

router = APIRouter(
    prefix="/queue",
    tags=["Queue"]
)


@router.get("/realtime/{session_id}", response_model=QueueRealtimeResponse)
def get_realtime_queue(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
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
    queue_result = queue_service.get_realtime_queue_metrics(current_user.uid, session_id)

    if queue_result is None:
        raise HTTPException(
            status_code=404,
            detail="No existen datos suficientes para calcular el modelo de colas."
        )

    return queue_result