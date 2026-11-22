from business_object.niveau_habilitation import NiveauHabilitation
from fastapi import APIRouter, Depends, HTTPException
from schema.utilisateur_model import (
    ModificationRoleModel,
    UtilisateurModel,
)
from service.utilisateur_service import UtilisateurService
from utils.authentication import (
    get_utilisateur_service,
)
from utils.log_utils import get_logger
from utils.verification_habilitation import require_niveau

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", tags=["Utilisateurs"])
def creer_compte(
    informations: UtilisateurModel,
    service: UtilisateurService = Depends(get_utilisateur_service),  # ruff: ignore[fast-api-non-annotated-dependency, function-call-in-default-argument]
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
    administrateur=Depends(  # ruff: ignore[function-call-in-default-argument]
        require_niveau(NiveauHabilitation.ADMIN)  # ruff: ignore[function-call-in-default-argument]
    ),
    service=Depends(get_utilisateur_service),  # ruff: ignore[function-call-in-default-argument]
):
    """Modifie le niveau d'habilitation d'un utilisateur."""

    logger.info(
        f"Modification du rôle de l'utilisateur "
        f"{informations.id_utilisateur}"
    )

    try:
        succes = service.modifier_habilitation(
            administrateur,
            informations.id_utilisateur,
            informations.nouvelle_habilitation,
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e),
        ) from e

    if not succes:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable ou échec de la mise à jour",
        )

    return {
        "detail": "Habilitation modifiée avec succès"
    }

def _valeur(attribut):
    """Renvoie la valeur d'une propriété, ou le résultat d'une méthode."""
    return attribut() if callable(attribut) else attribut


@router.get("/me", tags=["Utilisateurs"])
def moi(
    utilisateur=Depends(require_niveau(NiveauHabilitation.CLIENT)),  # noqa: B008
):
    """Retourne les informations de l'utilisateur connecté."""
    pseudo = _valeur(utilisateur.get_pseudo)
    id_utilisateur = _valeur(utilisateur.get_id_utilisateur)
    niveau = _valeur(utilisateur.get_niveau)

    logger.info("Informations de l'utilisateur %s", pseudo)

    return {
        "id_utilisateur": id_utilisateur,
        "pseudo": pseudo,
        "niveau": getattr(niveau, "name", str(niveau)),
    }