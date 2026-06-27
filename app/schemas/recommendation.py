from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    title: str
    description: str
    priority: str
    metric_reference: Optional[str] = None


class RecommendationResponse(BaseModel):
    session_id: str

    overall_status: str
    congestion_probability_pct: float

    summary: str
    recommendations: List[RecommendationItem]

    generated_by: str
    generated_at: datetime