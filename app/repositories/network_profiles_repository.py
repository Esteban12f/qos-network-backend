from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.future_database_models import (
    NetworkProfileDB,
    NetworkSessionDB,
)


class NetworkProfilesRepository:

    def confirm_for_session(
        self,
        user_id: str,
        session_id: str,
        name: str,
        normalized_name: str,
        network_type: str | None,
    ) -> dict:
        """
        Crea o reutiliza un perfil de red y lo relaciona con session_id.

        Si el usuario ya tenía un perfil con el mismo nombre,
        no se duplica.
        """

        now = datetime.now(timezone.utc)

        with SessionLocal() as db:
            profile = (
                db.query(NetworkProfileDB)
                .filter(
                    NetworkProfileDB.user_id == user_id,
                    NetworkProfileDB.normalized_name
                    == normalized_name,
                )
                .first()
            )

            if profile is None:
                profile = NetworkProfileDB(
                    user_id=user_id,
                    name=name,
                    normalized_name=normalized_name,
                    network_type=network_type,
                    created_at=now,
                    updated_at=now,
                )

                db.add(profile)
                db.flush()

            else:
                # Mantiene la escritura más reciente del nombre.
                profile.name = name

                if network_type is not None:
                    profile.network_type = network_type

                profile.updated_at = now

            session_link = (
                db.query(NetworkSessionDB)
                .filter(
                    NetworkSessionDB.user_id == user_id,
                    NetworkSessionDB.session_id == session_id,
                )
                .first()
            )

            if session_link is None:
                session_link = NetworkSessionDB(
                    user_id=user_id,
                    session_id=session_id,
                    network_profile_id=profile.id,
                    started_at=now,
                    updated_at=now,
                )

                db.add(session_link)

            else:
                session_link.network_profile_id = profile.id
                session_link.updated_at = now

            db.commit()
            db.refresh(profile)
            db.refresh(session_link)

            return self._session_to_dict(
                profile,
                session_link,
            )

    def get_for_session(
        self,
        user_id: str,
        session_id: str,
    ) -> Optional[dict]:
        with SessionLocal() as db:
            row = (
                db.query(
                    NetworkProfileDB,
                    NetworkSessionDB,
                )
                .join(
                    NetworkSessionDB,
                    NetworkSessionDB.network_profile_id
                    == NetworkProfileDB.id,
                )
                .filter(
                    NetworkSessionDB.user_id == user_id,
                    NetworkSessionDB.session_id == session_id,
                    NetworkProfileDB.user_id == user_id,
                )
                .first()
            )

            if row is None:
                return None

            profile, session_link = row

            return self._session_to_dict(
                profile,
                session_link,
            )

    def list_for_user(
        self,
        user_id: str,
    ) -> list[dict]:
        with SessionLocal() as db:
            rows = (
                db.query(
                    NetworkProfileDB,
                    func.count(
                        NetworkSessionDB.id
                    ).label("session_count"),
                    func.max(
                        NetworkSessionDB.updated_at
                    ).label("last_used_at"),
                )
                .outerjoin(
                    NetworkSessionDB,
                    NetworkSessionDB.network_profile_id
                    == NetworkProfileDB.id,
                )
                .filter(
                    NetworkProfileDB.user_id == user_id
                )
                .group_by(NetworkProfileDB.id)
                .order_by(
                    func.max(
                        NetworkSessionDB.updated_at
                    ).desc().nullslast(),
                    NetworkProfileDB.name.asc(),
                )
                .all()
            )

            return [
                {
                    "id": profile.id,
                    "name": profile.name,
                    "network_type": profile.network_type,
                    "session_count": int(session_count or 0),
                    "last_used_at": last_used_at,
                    "created_at": profile.created_at,
                    "updated_at": profile.updated_at,
                }
                for profile, session_count, last_used_at in rows
            ]

    @staticmethod
    def _session_to_dict(
        profile: NetworkProfileDB,
        session_link: NetworkSessionDB,
    ) -> dict:
        return {
            "id": profile.id,
            "name": profile.name,
            "network_type": profile.network_type,
            "session_id": session_link.session_id,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "session_started_at": session_link.started_at,
            "session_updated_at": session_link.updated_at,
        }


network_profiles_repository = NetworkProfilesRepository()