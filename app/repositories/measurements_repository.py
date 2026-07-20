from typing import List, Optional
from app.core.database import SessionLocal
from app.models.future_database_models import MeasurementDB

class MeasurementsRepository:

    def save(self, user_id: str, session_id: str, measurement: dict) -> dict:
        with SessionLocal() as db:
            db.add(MeasurementDB(user_id=user_id, **measurement))
            db.commit()
        return measurement

    def get_latest(self, user_id: str, session_id: str) -> Optional[dict]:
        with SessionLocal() as db:
            row = (db.query(MeasurementDB)
                   .filter(MeasurementDB.user_id == user_id, MeasurementDB.session_id == session_id)
                   .order_by(MeasurementDB.id.desc()).first())
            return self._to_dict(row) if row else None

    def get_history(self, user_id: str, session_id: str) -> List[dict]:
        with SessionLocal() as db:
            rows = (db.query(MeasurementDB)
                    .filter(MeasurementDB.user_id == user_id, MeasurementDB.session_id == session_id)
                    .order_by(MeasurementDB.id.asc()).all())
            return [self._to_dict(r) for r in rows]

    def count(self, user_id: str, session_id: str) -> int:
        with SessionLocal() as db:
            return (db.query(MeasurementDB)
                    .filter(MeasurementDB.user_id == user_id, MeasurementDB.session_id == session_id)
                    .count())

    def exists(self, user_id: str, session_id: str) -> bool:
        with SessionLocal() as db:
            return (db.query(MeasurementDB.id)
                    .filter(MeasurementDB.user_id == user_id, MeasurementDB.session_id == session_id)
                    .first() is not None)

    def clear_session(self, user_id: str, session_id: str) -> bool:
        with SessionLocal() as db:
            deleted = (db.query(MeasurementDB)
                       .filter(MeasurementDB.user_id == user_id, MeasurementDB.session_id == session_id)
                       .delete())
            db.commit()
            return deleted > 0

    def clear_all(self, user_id: str) -> None:
        with SessionLocal() as db:
            db.query(MeasurementDB).filter(MeasurementDB.user_id == user_id).delete()
            db.commit()

    def get_all_session_ids(self, user_id: str) -> List[str]:
        with SessionLocal() as db:
            return [r[0] for r in (db.query(MeasurementDB.session_id)
                                   .filter(MeasurementDB.user_id == user_id)
                                   .distinct().all())]

    @staticmethod
    def _to_dict(row: MeasurementDB) -> dict:
        return {c.name: getattr(row, c.name) for c in row.__table__.columns}

measurements_repository = MeasurementsRepository()
