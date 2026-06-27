from collections import defaultdict, deque
from threading import Lock
from typing import Dict, List, Optional


class MeasurementsRepository:
    """
    Repositorio temporal en memoria.

    Guarda las mediciones por session_id.
    Más adelante este repositorio podrá reemplazarse por PostgreSQL
    sin cambiar la lógica de los servicios.
    """

    def __init__(self, max_points_per_session: int = 300):
        self.max_points_per_session = max_points_per_session
        self._storage: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self.max_points_per_session)
        )
        self._lock = Lock()

    def save(self, session_id: str, measurement: dict) -> dict:
        """
        Guarda una medición asociada a una sesión.
        """
        with self._lock:
            self._storage[session_id].append(measurement)

        return measurement

    def get_latest(self, session_id: str) -> Optional[dict]:
        """
        Devuelve la última medición registrada para una sesión.
        """
        with self._lock:
            session_measurements = self._storage.get(session_id)

            if not session_measurements:
                return None

            return session_measurements[-1]

    def get_history(self, session_id: str) -> List[dict]:
        """
        Devuelve todo el historial almacenado para una sesión.
        """
        with self._lock:
            session_measurements = self._storage.get(session_id)

            if not session_measurements:
                return []

            return list(session_measurements)

    def count(self, session_id: str) -> int:
        """
        Devuelve la cantidad de mediciones registradas para una sesión.
        """
        with self._lock:
            session_measurements = self._storage.get(session_id)

            if not session_measurements:
                return 0

            return len(session_measurements)

    def exists(self, session_id: str) -> bool:
        """
        Verifica si una sesión tiene mediciones.
        """
        with self._lock:
            return session_id in self._storage and len(self._storage[session_id]) > 0

    def clear_session(self, session_id: str) -> bool:
        """
        Elimina las mediciones de una sesión específica.
        """
        with self._lock:
            if session_id in self._storage:
                del self._storage[session_id]
                return True

            return False

    def clear_all(self) -> None:
        """
        Limpia todas las mediciones almacenadas.
        """
        with self._lock:
            self._storage.clear()

    def get_all_session_ids(self) -> List[str]:
        """
        Devuelve todos los session_id registrados.
        """
        with self._lock:
            return list(self._storage.keys())


measurements_repository = MeasurementsRepository()