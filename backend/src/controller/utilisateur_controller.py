from fastapi import APIRouter, Depends, HTTPException

from schema.utilisateur_model import (
    ModificationRoleModel,
    UtilisateurModel,
)
from service.utilisateur_service import UtilisateurService
from utils.authentication import (
    get_utilisateur_service,
    get_current_user,
)
from utils.log_utils import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", tags=["Utilisateurs"])
def creer_compte(
    informations: UtilisateurModel,
    service: UtilisateurService = Depends(get_utilisateur_service),
):
    """Crée un compte utilisateur."""

    logger.info("Création d'un compte")

    try:
        utilisateur = service.creer_compte(
            informations.pseudo,
            informations.mdp,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return utilisateur


@router.put("/role", tags=["Utilisateurs"])
def modifier_role(
    informations: ModificationRoleModel,
    utilisateur=Depends(get_current_user),
    service: UtilisateurService = Depends(get_utilisateur_service),
):
    """Modifie le niveau d'habilitation d'un utilisateur."""

    logger.info(
        f"Modification du rôle de l'utilisateur "
        f"{informations.id_utilisateur}"
    )

    try:
        succes = service.modifier_habilitation(
            utilisateur,
            informations.id_utilisateur,
            informations.nouvelle_habilitation,
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Seul un administrateur peut modifier les habilitations.",
        )

    if not succes:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable ou échec de la mise à jour",
        )

    return {
        "detail": "Habilitation modifiée avec succès"
    }