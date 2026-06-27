from collections import defaultdict, deque
from threading import Lock
from typing import Dict, List, Optional


class RecommendationsRepository:
    """
    Repositorio temporal en memoria para recomendaciones.

    En una versión futura, este repositorio podrá guardar
    recomendaciones históricas en PostgreSQL.
    """

    def __init__(self, max_recommendations_per_session: int = 100):
        self.max_recommendations_per_session = max_recommendations_per_session
        self._storage: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self.max_recommendations_per_session)
        )
        self._lock = Lock()

    def save(self, session_id: str, recommendation: dict) -> dict:
        """
        Guarda una recomendación asociada a una sesión.
        """
        with self._lock:
            self._storage[session_id].append(recommendation)

        return recommendation

    def get_latest(self, session_id: str) -> Optional[dict]:
        """
        Devuelve la última recomendación generada para una sesión.
        """
        with self._lock:
            session_recommendations = self._storage.get(session_id)

            if not session_recommendations:
                return None

            return session_recommendations[-1]

    def get_history(self, session_id: str) -> List[dict]:
        """
        Devuelve el historial de recomendaciones de una sesión.
        """
        with self._lock:
            session_recommendations = self._storage.get(session_id)

            if not session_recommendations:
                return []

            return list(session_recommendations)

    def clear_session(self, session_id: str) -> bool:
        """
        Elimina las recomendaciones de una sesión.
        """
        with self._lock:
            if session_id in self._storage:
                del self._storage[session_id]
                return True

            return False

    def clear_all(self) -> None:
        """
        Limpia todas las recomendaciones almacenadas.
        """
        with self._lock:
            self._storage.clear()


recommendations_repository = RecommendationsRepository()