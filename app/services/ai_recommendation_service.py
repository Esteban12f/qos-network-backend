from typing import Optional
from datetime import datetime, timezone

from app.repositories.recommendations_repository import recommendations_repository
from app.schemas.recommendation import (
    RecommendationItem,
    RecommendationResponse,
)
from app.services.queue_service import queue_service
from app.services.statistics_service import statistics_service


class AIRecommendationService:
    """
    Servicio genérico de recomendaciones.

    Este servicio no consume IA externa.
    Genera recomendaciones básicas a partir de:
    - estadísticas reales
    - métricas QoS
    - modelo de colas M/M/1

    Cuando se implemente IA generativa, este archivo puede ser reemplazado
    sin cambiar el endpoint /recommendations/{session_id}.
    """

    def generate_recommendations(self, user_id: str, session_id: str) -> Optional[RecommendationResponse]:
        stats = statistics_service.get_statistics(user_id, session_id)
        queue_metrics = queue_service.get_realtime_queue_metrics(user_id, session_id)

        if stats is None or queue_metrics is None:
            return None

        recommendations = self._build_generic_recommendations(
            latency_mean=stats.latency_stats.mean,
            jitter_mean=stats.jitter_stats.mean,
            download_mean=stats.download_stats.mean,
            packet_loss_mean=stats.packet_loss_stats.mean,
            rho_pct=queue_metrics.rho_pct,
            congestion_probability_pct=queue_metrics.congestion_probability_pct,
            traffic_trend=stats.traffic_trend,
        )

        summary = self._build_summary(
            overall_status=queue_metrics.stability_status,
            congestion_probability_pct=queue_metrics.congestion_probability_pct,
            traffic_trend=stats.traffic_trend,
        )

        response = RecommendationResponse(
            session_id=session_id,
            overall_status=queue_metrics.stability_status,
            congestion_probability_pct=queue_metrics.congestion_probability_pct,
            summary=summary,
            recommendations=recommendations,
            generated_by="generic_recommendation_service",
            generated_at=datetime.now(timezone.utc)
        )

        recommendations_repository.save(
            session_id=session_id,
            recommendation=response.model_dump()
        )

        return response

    def _build_generic_recommendations(
        self,
        latency_mean: float,
        jitter_mean: float,
        download_mean: float,
        packet_loss_mean: float,
        rho_pct: float,
        congestion_probability_pct: float,
        traffic_trend: str,
    ) -> list[RecommendationItem]:

        recommendations: list[RecommendationItem] = []

        if latency_mean > 120:
            recommendations.append(
                RecommendationItem(
                    title="Latencia elevada",
                    description=(
                        "La latencia promedio se encuentra por encima de un nivel recomendable. "
                        "Se sugiere revisar la estabilidad de la conexión, cerrar aplicaciones que consuman red "
                        "y evitar descargas pesadas durante actividades sensibles al retardo."
                    ),
                    priority="warning",
                    metric_reference="latency"
                )
            )
        else:
            recommendations.append(
                RecommendationItem(
                    title="Latencia dentro de rango aceptable",
                    description=(
                        "La latencia promedio se mantiene en un rango adecuado para navegación general "
                        "y servicios comunes. Se recomienda continuar el monitoreo para detectar variaciones."
                    ),
                    priority="success",
                    metric_reference="latency"
                )
            )

        if jitter_mean > 30:
            recommendations.append(
                RecommendationItem(
                    title="Variación de latencia considerable",
                    description=(
                        "El jitter presenta variaciones que podrían afectar videollamadas, juegos en línea "
                        "o servicios en tiempo real. Se recomienda usar una conexión más estable o acercarse al router."
                    ),
                    priority="warning",
                    metric_reference="jitter"
                )
            )

        if packet_loss_mean > 5:
            recommendations.append(
                RecommendationItem(
                    title="Pérdida aproximada elevada",
                    description=(
                        "Se detectan fallos o timeouts en las solicitudes de prueba. Esto puede estar relacionado "
                        "con saturación, interferencia Wi-Fi o inestabilidad temporal de la red."
                    ),
                    priority="critical",
                    metric_reference="packet_loss"
                )
            )

        if download_mean < 5:
            recommendations.append(
                RecommendationItem(
                    title="Throughput bajo",
                    description=(
                        "La velocidad de descarga medida es baja. Se recomienda reducir dispositivos conectados, "
                        "evitar tráfico pesado y verificar si la red Wi-Fi presenta baja señal."
                    ),
                    priority="warning",
                    metric_reference="throughput"
                )
            )

        if rho_pct >= 80:
            recommendations.append(
                RecommendationItem(
                    title="Alta utilización según M/M/1",
                    description=(
                        "El modelo de colas M/M/1 indica alta utilización del sistema. "
                        "Se recomienda reducir tráfico no crítico y priorizar aplicaciones sensibles a latencia."
                    ),
                    priority="critical",
                    metric_reference="rho"
                )
            )
        elif rho_pct >= 50:
            recommendations.append(
                RecommendationItem(
                    title="Utilización moderada",
                    description=(
                        "La utilización estimada no es crítica, pero conviene mantener monitoreo continuo "
                        "para evitar degradación si aumenta la demanda de red."
                    ),
                    priority="info",
                    metric_reference="rho"
                )
            )

        if congestion_probability_pct >= 70:
            recommendations.append(
                RecommendationItem(
                    title="Probabilidad de congestión alta",
                    description=(
                        "La probabilidad estimada de congestión es alta. Se recomienda evitar descargas, "
                        "streaming en alta calidad o transferencias grandes mientras se realizan tareas críticas."
                    ),
                    priority="critical",
                    metric_reference="queue"
                )
            )

        if traffic_trend == "CRECIENTE":
            recommendations.append(
                RecommendationItem(
                    title="Tendencia de latencia creciente",
                    description=(
                        "La latencia muestra una tendencia creciente. Esto puede indicar degradación progresiva "
                        "de la conexión durante la ventana analizada."
                    ),
                    priority="warning",
                    metric_reference="latency"
                )
            )

        if not recommendations:
            recommendations.append(
                RecommendationItem(
                    title="Conexión estable",
                    description=(
                        "Las métricas actuales no muestran señales importantes de congestión. "
                        "Se recomienda mantener el monitoreo para validar el comportamiento en distintos horarios."
                    ),
                    priority="success",
                    metric_reference="general"
                )
            )

        return recommendations[:5]

    def _build_summary(
        self,
        overall_status: str,
        congestion_probability_pct: float,
        traffic_trend: str,
    ) -> str:
        return (
            f"Diagnóstico generado a partir de métricas reales del navegador, "
            f"análisis estadístico y modelo M/M/1. "
            f"Estado general: {overall_status}. "
            f"Probabilidad estimada de congestión: {round(congestion_probability_pct, 2)}%. "
            f"Tendencia observada: {traffic_trend}."
        )


ai_recommendation_service = AIRecommendationService()