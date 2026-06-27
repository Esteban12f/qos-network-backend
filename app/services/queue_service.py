from app.services.statistics_service import statistics_service
from app.schemas.queue import QueueRealtimeResponse


class QueueService:
    """
    Servicio encargado de aplicar el modelo M/M/1.

    En este enfoque web:
    - λ representa la tasa promedio de solicitudes de prueba por segundo.
    - μ se estima a partir de la latencia promedio.
    """

    def get_realtime_queue_metrics(self, session_id: str) -> QueueRealtimeResponse | None:
        stats = statistics_service.get_statistics(session_id)

        if stats is None:
            return None

        lambda_rate = stats.lambda_rate
        mean_latency_ms = stats.latency_stats.mean

        mu_rate = self._estimate_mu_rate(mean_latency_ms)

        if mu_rate <= 0:
            rho = 0
        else:
            rho = lambda_rate / mu_rate

        is_stable = rho < 1

        if is_stable and mu_rate > lambda_rate:
            l = lambda_rate / (mu_rate - lambda_rate)
            lq = (lambda_rate ** 2) / (mu_rate * (mu_rate - lambda_rate))
            w = 1 / (mu_rate - lambda_rate)
            wq = lambda_rate / (mu_rate * (mu_rate - lambda_rate))

            w_ms = w * 1000
            wq_ms = wq * 1000
        else:
            l = 999999.0
            lq = 999999.0
            w_ms = 999999.0
            wq_ms = 999999.0

        congestion_probability = self._estimate_congestion_probability(
            rho=rho,
            latency_mean=stats.latency_stats.mean,
            jitter_mean=stats.jitter_stats.mean,
            packet_loss_mean=stats.packet_loss_stats.mean
        )

        stability_status = self._get_stability_status(rho)

        return QueueRealtimeResponse(
            session_id=session_id,

            lambda_rate=round(lambda_rate, 4),
            mu_rate=round(mu_rate, 4),

            rho=round(rho, 4),
            rho_pct=round(rho * 100, 2),

            l=round(l, 4),
            lq=round(lq, 4),
            w_ms=round(w_ms, 4),
            wq_ms=round(wq_ms, 4),

            is_stable=is_stable,
            stability_status=stability_status,

            congestion_probability=round(congestion_probability, 4),
            congestion_probability_pct=round(congestion_probability * 100, 2),

            analysis_message=self._build_queue_message(
                rho=rho,
                congestion_probability=congestion_probability
            )
        )

    def _estimate_mu_rate(self, mean_latency_ms: float) -> float:
        """
        Estima μ como capacidad aproximada de atención de solicitudes por segundo.

        Si la latencia promedio es 100 ms:
        μ ≈ 1000 / 100 = 10 solicitudes/s
        """
        if mean_latency_ms <= 0:
            return 0

        return 1000 / mean_latency_ms

    def _estimate_congestion_probability(
        self,
        rho: float,
        latency_mean: float,
        jitter_mean: float,
        packet_loss_mean: float
    ) -> float:
        """
        Estimación probabilística de congestión basada en métricas normalizadas.

        No genera recomendaciones. Solo calcula probabilidad.
        """
        rho_score = min(rho, 1.5) / 1.5
        latency_score = min(latency_mean, 300) / 300
        jitter_score = min(jitter_mean, 100) / 100
        loss_score = min(packet_loss_mean, 20) / 20

        probability = (
            0.45 * rho_score +
            0.25 * latency_score +
            0.20 * jitter_score +
            0.10 * loss_score
        )

        return max(0, min(probability, 1))

    def _get_stability_status(self, rho: float) -> str:
        if rho < 0.5:
            return "ESTABLE"

        if rho < 0.8:
            return "ADVERTENCIA"

        if rho < 1:
            return "ALTA_UTILIZACION"

        return "INESTABLE"

    def _build_queue_message(self, rho: float, congestion_probability: float) -> str:
        if rho >= 1:
            return "El sistema presenta una condición inestable según el modelo M/M/1."

        if congestion_probability >= 0.75:
            return "Existe una alta probabilidad de congestión en los próximos instantes."

        if congestion_probability >= 0.5:
            return "Existe una probabilidad moderada de degradación de la conexión."

        return "El sistema se mantiene dentro de un comportamiento aceptable según las métricas actuales."


queue_service = QueueService()