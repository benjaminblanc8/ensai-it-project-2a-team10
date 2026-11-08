from fastapi import APIRouter, Depends, HTTPException
from schema.gare_model import GareReadModel
from service.api_sncf_service import ApiSncfService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_api_sncf_service():
    """Injecte la dépendance au service API SNCF."""
    return ApiSncfService()


@router.get("/{nom_gare}", response_model=list[GareReadModel], tags=["API SNCF"])
def rechercher_gare_par_nom(
    nom_gare: str,
    service=Depends(get_api_sncf_service),  # noqa: B008
):
    """Recherche de gares par leur nom."""

    logger.info("Recherche de gares : %s", nom_gare)

    list_gare = service.obtenir_arrets_par_nom(nom_gare)

    if list_gare == []:
        raise HTTPException(status_code=404, detail="Gares introuvables")

    return list_gare
