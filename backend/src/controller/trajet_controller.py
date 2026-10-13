from fastapi import APIRouter
from service.gare_service import GareService
from service.ligne_service import LigneService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_ligne_service():
    """Injecte la dépendance au service ligne."""
    return LigneService()


def get_gare_service():
    """Injecte la dépendance au service gare."""
    return GareService()
