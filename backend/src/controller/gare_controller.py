from fastapi import APIRouter
from service.gare_service import GareService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_gare_service():
    """Injecte la dépendance au service gare"""
    return GareService()


async def recherche_gare(nom_gare: str):
    """Renvoie la gare ayant le nom nom_gare si elle existe
    Retourne : Gare
    ou lève une exception si elle n'existe pas
    """


async def ajouter_gare(nom_gare: str):
    """Ajoute une gare ayant le nom nom_gare à la base de données"""


async def supprimer_gare(nom_gare: str):
    """Supprime la gare ayant le nom nom_gare si elle existe
    Sinon, ne fait rien"""
