from pydantic import BaseModel


class QueueRealtimeResponse(BaseModel):
    session_id: str

    lambda_rate: float
    mu_rate: float

    rho: float
    rho_pct: float

    l: float
    lq: float
    w_ms: float
    wq_ms: float

    is_stable: bool
    stability_status: str

    congestion_probability: float
    congestion_probability_pct: float

    analysis_message: str