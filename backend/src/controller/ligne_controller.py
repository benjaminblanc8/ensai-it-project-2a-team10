from business_object.gare import Gare
from fastapi import APIRouter
from service.ligne_service import LigneService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_ligne_service():
    """Injecte la dépendance au service ligne"""
    return LigneService()


async def recherche_ligne():
    pass


async def creer_ligne(gare_depart: Gare, gare_arrivee: Gare):
    """Ajoute à la base de données la ligne d'exploitation reliant gare_depart à gare_arrivee"""


async def modifier_ligne():
    pass


async def supprimer_ligne():
    pass
