from fastapi import APIRouter, Depends, HTTPException

from app.core.firebase_auth import CurrentUser, get_current_user
from app.schemas.recommendation import RecommendationResponse
from app.services.ai_recommendation_service import ai_recommendation_service

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/{session_id}", response_model=RecommendationResponse)
def get_recommendations(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Genera recomendaciones basadas en las métricas reales de la sesión.

    El servicio queda preparado para conectarse posteriormente con IA.
    """
    recommendation_result = ai_recommendation_service.generate_recommendations(current_user.uid, session_id)

    if recommendation_result is None:
        raise HTTPException(
            status_code=404,
            detail="No existen datos suficientes para generar recomendaciones."
        )

    return recommendation_result