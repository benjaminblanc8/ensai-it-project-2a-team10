from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from service.utilisateur_service import UtilisateurService
from utils.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/connexion/"
)

def get_utilisateur_service():
    """Injecte la dépendance au service utilisateur."""
    return UtilisateurService()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: UtilisateurService = Depends(get_utilisateur_service),
):
    """Vérifie le JWT et retourne l'utilisateur connecté."""

    try:
        payload = decode_access_token(token)

        utilisateur_id = int(payload["sub"])

    except (JWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    utilisateur = service.get_by_id(utilisateur_id)


    return utilisateur