from business_object.gare import Gare
from business_object.niveau_habilitation import NiveauHabilitation
from fastapi import APIRouter, Depends, HTTPException
from schema.gare_model import GareModel, GareReadModel
from service.api_sncf_service import ApiSncfService
from service.gare_service import GareService
from utils.log_utils import get_logger
from utils.verification_habilitation import require_niveau

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
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),  # ruff: ignore[function-call-in-default-argument]
    service=Depends(get_gare_service),  # noqa: B008
):
    """Ajoute une gare."""
    logger.info("Ajout d'une gare")

    gare = Gare(
        id_gare=None,
        nom=informations.nom,
        ville=informations.ville,
<<<<<<< HEAD
<<<<<<< HEAD
        # id_gare_sncf=informations.id_gare_sncf,
=======
        id_gare_sncf=informations.id_gare_sncf,
>>>>>>> 3dc196c55a97a0fefedaf66fc3261fb7b634a0ee
=======
>>>>>>> cec5de455a471dd683e6959242a26f3f46f09806
    )

    return service.ajout_gare(gare)


@router.get("/id/{id_gare}", response_model=GareReadModel, tags=["Gares"])
def rechercher_gare_par_id(
    id_gare: int,
    service=Depends(get_gare_service),  # noqa: B008
):
    """Recherche une gare par son identifiant."""

    logger.info("Recherche d'une gare")

    gare = service.recherche_gare(id_gare)

    if gare is None:
        raise HTTPException(status_code=404, detail="Gare introuvable")

    return gare

@router.get("/nom_gare/{nom_gare}", response_model=list[GareReadModel], tags=["Gares"])
def rechercher_gare_par_nom(
    nom_gare: str,
    service=Depends(get_gare_service),  # noqa: B008
):
    """Recherche une gare par son nom."""

    logger.info("Recherche d'une gare")

    list_gare = service.recherche_gare_par_nom(nom_gare)

    if len(list_gare)==0:
        raise HTTPException(status_code=404, detail="Gares introuvables")

    return list_gare


@router.delete("/{id_gare}", response_model=GareReadModel, tags=["Gares"])
def supprimer_gare(
    id_gare: int,
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),  # ruff: ignore[function-call-in-default-argument]
    service=Depends(get_gare_service),  # noqa: B008
):
    """Supprime une gare."""

    logger.info("Suppression d'une gare")

    return service.supprimer_gare(id_gare)
