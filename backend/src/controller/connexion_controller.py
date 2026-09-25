from fastapi import APIRouter, Depends
from schema.utilisateur_model import UtilisateurModel
from service.utilisateur_service import UtilisateurService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_utilisateur_service():
    """Injecte la dépendance au service utilisateur"""
    return UtilisateurService()


@router.post("/", tags=["Login"])
def connexion(informations: UtilisateurModel, service=Depends(get_utilisateur_service)):
    """à compléter"""
