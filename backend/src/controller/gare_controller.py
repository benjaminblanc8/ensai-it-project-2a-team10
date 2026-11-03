from business_object.gare import Gare
from fastapi import APIRouter, Depends
from schema.gare_model import GareListModel, GareModel, GareReadModel
from service.gare_service import GareService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_gare_service():
    """Injecte la dépendance au service gare."""
    return GareService()


def get_api_sncf_service():
    """Injecte la dépendance au service API SNCF."""
    return ApiSncfService()


@router.post("/", response_model=GareReadModel, tags=["Gares"])
def ajouter_gare(
    informations: GareModel,
    service=Depends(get_gare_service),  # noqa: B008
):
    """Ajoute une gare."""

    logger.info("Ajout d'une gare")

    gare = Gare(
        id_gare=None,
        nom=informations.nom,
        ville=informations.ville,
        latitude=informations.latitude,
        longitude=informations.longitude,
    )

    return service.ajout_gare(gare)


@router.get("/id/{id_gare}", response_model=GareReadModel, tags=["Gares"])
def rechercher_gare_par_id(
    id_gare: int,
    service=Depends(get_gare_service),  # noqa: B008
):
    """Recherche une gare par son identifiant."""

    logger.info("Recherche d'une gare")

    return service.recherche_gare(id_gare)


@router.get("/nom_gare/{nom_gare}", response_model=GareListModel, tags=["Gares"])
def rechercher_gare_par_nom(
    nom_gare: str,
    service=Depends(get_api_sncf_service),  # noqa: B008
):
    """Recherche une gare par son nom."""

    logger.info("Recherche d'une gare")

    return service.obtenir_arrets_par_nom(nom_gare)


@router.delete("/{id_gare}", response_model=GareReadModel, tags=["Gares"])
def supprimer_gare(
    id_gare: int,
    service=Depends(get_gare_service),  # noqa: B008
):
    """Supprime une gare."""

    logger.info("Suppression d'une gare")

    return service.supprimer_gare(id_gare)
