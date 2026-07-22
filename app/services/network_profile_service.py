from app.repositories.network_profiles_repository import (
    network_profiles_repository,
)
from app.schemas.network_profile import (
    NetworkProfileConfirmRequest,
)


class NetworkProfileService:

    def confirm_network(
        self,
        user_id: str,
        session_id: str,
        payload: NetworkProfileConfirmRequest,
    ) -> dict:
        clean_session_id = session_id.strip()

        if len(clean_session_id) < 3:
            raise ValueError(
                "El identificador de sesión no es válido."
            )

        display_name = " ".join(payload.name.split())
        normalized_name = display_name.casefold()

        return network_profiles_repository.confirm_for_session(
            user_id=user_id,
            session_id=clean_session_id,
            name=display_name,
            normalized_name=normalized_name,
            network_type=payload.network_type,
        )

    def get_network_for_session(
        self,
        user_id: str,
        session_id: str,
    ) -> dict | None:
        return network_profiles_repository.get_for_session(
            user_id=user_id,
            session_id=session_id,
        )

    def list_user_networks(
        self,
        user_id: str,
    ) -> list[dict]:
        return network_profiles_repository.list_for_user(
            user_id=user_id
        )


network_profile_service = NetworkProfileService()