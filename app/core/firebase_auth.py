from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config import get_settings

_bearer_scheme = HTTPBearer(auto_error=False)
_google_request = google_requests.Request()


@dataclass
class CurrentUser:
    uid: str
    email: str | None = None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    """
    Verifica el ID token de Firebase enviado en el header Authorization: Bearer <token>.

    La verificación se hace contra las claves públicas de Google (sin necesitar
    una service account key), validando que el token pertenezca al proyecto
    Firebase configurado en firebase_project_id.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autenticación.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings = get_settings()

    try:
        decoded_token = id_token.verify_firebase_token(
            credentials.credentials,
            _google_request,
            audience=settings.firebase_project_id,
        )
    except (ValueError, GoogleAuthError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    uid = decoded_token.get("user_id") or decoded_token.get("sub")

    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no contiene un identificador de usuario válido.",
        )

    return CurrentUser(uid=uid, email=decoded_token.get("email"))
