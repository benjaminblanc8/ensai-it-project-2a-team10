from fastapi import APIRouter, Depends, HTTPException
from schema.ligne_model import LigneModel, LigneReadModel, LigneUpdateModel, LigneReadUpdateModel
from service.gare_service import GareService
from service.ligne_service import LigneService
from utils.log_utils import get_logger
from utils.verification_habilitation import require_niveau
from business_object.niveau_habilitation import NiveauHabilitation 

router = APIRouter()

logger = get_logger(__name__)


def get_ligne_service():
    """Injecte la dépendance au service ligne."""
    return LigneService()


def get_gare_service():
    """Injecte la dépendance au service gare."""
    return GareService()


@router.post("/", response_model=LigneReadModel, tags=["Lignes"])
def creer_ligne(
    informations: LigneModel,
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),
    ligne_service=Depends(get_ligne_service),  # noqa: B008
):
    """Crée une ligne entre deux gares."""

    logger.info("Création d'une ligne")

    gare_depart = ligne_service.gare_service.recherche_gare(informations.id_gare_depart)

    gare_arrivee = ligne_service.gare_service.recherche_gare(
        informations.id_gare_arrivee
    )

    return ligne_service.creer(gare_depart, gare_arrivee)


@router.get("/{id_ligne}", response_model=LigneReadModel, tags=["Lignes"])
def rechercher_ligne(
    id_ligne: int,
    service=Depends(get_ligne_service),  # noqa: B008
):
    """Recherche une ligne par son identifiant."""

    logger.info("Recherche d'une ligne")

    ligne = service.rechercher_ligne(id_ligne)

    if not ligne:
        raise HTTPException(status_code=404, detail="Ligne introuvable")

    return ligne

@router.put("/{id_ligne}", response_model=LigneReadUpdateModel, tags=["Lignes"])
def modifier_ligne(
    informations: LigneUpdateModel,
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),
    service=Depends(get_ligne_service),
):
    """ Modifie une ligne """

    logger.info("Modification d'une ligne")

    gare_depart = service.gare_service.recherche_gare(informations.id_gare_depart)

    gare_arrivee = service.gare_service.recherche_gare(
        informations.id_gare_arrivee
    )

    return service.modifier_ligne(informations.id_ligne, gare_depart, gare_arrivee)


@router.delete("/{id_ligne}", response_model=LigneReadModel, tags=["Lignes"])
def supprimer_ligne(
    id_ligne: int,
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),
    service=Depends(get_ligne_service),  # noqa: B008
):
    """Supprime une ligne."""

    logger.info("Suppression d'une ligne")

    ligne = service.rechercher_ligne(id_ligne)

    if not ligne:
        raise HTTPException(status_code=404, detail="Ligne introuvable")

    service.supprimer_ligne(id_ligne)

    return ligne
