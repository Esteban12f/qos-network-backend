from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.core.firebase_auth import (
    CurrentUser,
    get_current_user,
)
from app.schemas.network_profile import (
    NetworkProfileConfirmRequest,
    NetworkProfileSessionResponse,
    NetworkProfilesListResponse,
)
from app.services.network_profile_service import (
    network_profile_service,
)


router = APIRouter(
    prefix="/network-profiles",
    tags=["Network Profiles"],
)


@router.put(
    "/session/{session_id}",
    response_model=NetworkProfileSessionResponse,
)
def confirm_network_for_session(
    session_id: str,
    payload: NetworkProfileConfirmRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Confirma el nombre de una red y la relaciona con una sesión.

    Si el usuario ya tiene una red con ese nombre,
    reutiliza el perfil existente.
    """

    try:
        return network_profile_service.confirm_network(
            user_id=current_user.uid,
            session_id=session_id,
            payload=payload,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/session/{session_id}",
    response_model=NetworkProfileSessionResponse,
)
def get_network_for_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Recupera la red asociada a un session_id.
    """

    profile = (
        network_profile_service.get_network_for_session(
            user_id=current_user.uid,
            session_id=session_id,
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No existe una red asociada "
                "a la sesión indicada."
            ),
        )

    return profile


@router.get(
    "",
    response_model=NetworkProfilesListResponse,
)
def list_user_networks(
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Devuelve todas las redes registradas por el usuario.
    """

    items = network_profile_service.list_user_networks(
        user_id=current_user.uid
    )

    return {
        "items": items,
        "total": len(items),
    }