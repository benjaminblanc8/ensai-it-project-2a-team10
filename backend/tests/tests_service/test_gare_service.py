from unittest.mock import MagicMock

from business_object.gare import Gare
from dao.gare_dao import GareDao
from service.gare_service import GareService

gare = Gare(id_gare=1, nom="gare de Rennes", ville="Rennes")


def test_ajout_gare_ok():

    # GIVEN
    id_gare, nom, ville = "1", "gare de Rennes", "Rennes"
    GareDao().creer_gare = MagicMock(return_value=True)
    # WHEN
    gare = GareService().ajout_gare(id_gare, nom, ville)
    # THEN
    assert isinstance(gare, Gare)
    assert gare.nom == nom


def test_ajout_gare_fail():

    # GIVEN
    id_gare, nom, ville = "1", "gare de Rennes", "Rennes"
    GareDao().creer_gare = MagicMock(return_value=False)
    # WHEN
    gare = GareService().ajout_gare(gare_test)
    # THEN
    assert gare is None


def test_recherche_gare():

    # GIVEN
    GareDao.recherche_gare = MagicMock(return_value=gare)
    # WHEN
    resultat = GareService().recherche_gare(id=9999)
    # THEN
    assert isinstance(resultat, Gare)
    assert resultat.nom == "gare de Rennes"
