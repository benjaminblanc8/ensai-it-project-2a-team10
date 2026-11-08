from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from service.utilisateur_service import UtilisateurService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_utilisateur_service():
    """Injecte la dépendance au service utilisateur."""
    return UtilisateurService()


@router.post("/", tags=["Connexion"])
def connexion(
    informations: OAuth2PasswordRequestForm = Depends(),  # ruff: ignore[fast-api-non-annotated-dependency, function-call-in-default-argument]
    service: UtilisateurService = Depends(get_utilisateur_service),  # ruff: ignore[fast-api-non-annotated-dependency, function-call-in-default-argument]
):
    """Connecte un utilisateur et retourne son token JWT."""

    logger.info("Connexion d'un utilisateur")

    utilisateur = service.connexion(
        informations.username,
        informations.password,
    )

    if not utilisateur:
        raise HTTPException(
            status_code=401,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return utilisateur
