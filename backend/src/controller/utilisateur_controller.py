from fastapi import APIRouter, Depends, HTTPException
from schema.utilisateur_model import ModificationRoleModel, UtilisateurModel
from service.utilisateur_service import UtilisateurService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_utilisateur_service():
    """Injecte la dépendance au service utilisateur."""
    return UtilisateurService()


@router.post("/", tags=["Utilisateurs"])
def creer_compte(
    informations: UtilisateurModel,
    service=Depends(get_utilisateur_service) # noqa: B008
):
    """Crée un compte utilisateur."""

    logger.info("Création d'un compte")

    utilisateur = service.creer_compte(
        informations.pseudo,
        informations.mdp
    )

    if not utilisateur:
        raise HTTPException(
            status_code=400,
            detail="Échec de la création du compte"
        )

    return utilisateur


@router.post("/connexion", tags=["Login"])
def connexion(
    informations: UtilisateurModel,
    service=Depends(get_utilisateur_service) # noqa: B008
):
    """Connecte un utilisateur."""

    logger.info("Connexion d'un utilisateur")

    utilisateur = service.connexion(
        informations.pseudo,
        informations.mdp
    )

    if not utilisateur:
        raise HTTPException(
            status_code=401,
            detail="Identifiants invalides"
        )

    return utilisateur


@router.put("/role", tags=["Utilisateurs"])
def modifier_role(
    informations: ModificationRoleModel,
    service=Depends(get_utilisateur_service) # noqa: B008
):
    """Modifie le niveau d'habilitation d'un utilisateur."""

    logger.info("Modification du rôle d'un utilisateur")

    raise HTTPException(
        status_code=501,
        detail="Fonctionnalité pas encore implémentée"
    )