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
    service=Depends(get_utilisateur_service),  # noqa: B008
):
    """Crée un compte utilisateur."""

    logger.info("Création d'un compte")

    try:
        utilisateur = service.creer_compte(informations.pseudo, informations.mdp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return utilisateur


@router.put("/role", tags=["Utilisateurs"])
def modifier_role(
    informations: ModificationRoleModel,
    service=Depends(get_utilisateur_service),  # noqa: B008
):
    """Modifie le niveau d'habilitation d'un utilisateur."""

    logger.info(f"Modification du rôle de l'utilisateur {informations.id_utilisateur}")

    # Récupérer l'administrateur qui fait la demande
    administrateur = service.rechercher_utilisateur(informations.id_administrateur)

    if administrateur is None:
        raise HTTPException(status_code=401, detail="Administrateur non reconnu")

    try:
        succes = service.modifier_habilitation(
            administrateur,
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
            status_code=404, detail="Utilisateur introuvable ou échec de la mise à jour"
        )

    return {"detail": "Habilitation modifiée avec succès"}
