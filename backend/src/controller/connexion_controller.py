from fastapi import APIRouter, Depends, HTTPException
from schema.utilisateur_model import UtilisateurModel
from service.utilisateur_service import UtilisateurService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_utilisateur_service():
    """Injecte la dépendance au service utilisateur."""
    return UtilisateurService()


@router.post("/", tags=["Connexion"])
def connexion(
    informations: UtilisateurModel,
    service=Depends(get_utilisateur_service),  # noqa: B008
):
    """Connecte un utilisateur et retourne ses informations."""

    logger.info("Connexion d'un utilisateur")

    utilisateur = service.connexion(informations.pseudo, informations.mdp)

    if not utilisateur:
        raise HTTPException(status_code=401, detail="Identifiants invalides")

    return utilisateur
