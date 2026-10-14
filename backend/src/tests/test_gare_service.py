from unittest.mock import MagicMock

from business_object.gare import Gare
from dao.gare_dao import GareDao
from service.gare_service import GareService


gare = Gare(id_gare=1,
            nom="gare de Rennes",
            ville="Rennes",
            latitude="48,1033° N",
            longitude="-1,6725° O")
 


def test_ajout_gare_ok():

    #GIVEN
    id_gare, nom, ville, latitude, longitude = 1, "gare de Rennes", "Rennes", "48,1033° N", "-1,6725° O"
    GareDao().create_gare = MagicMock(return_value=True)
    #WHEN
    gare = GareService().ajout_gare(id_gare, nom, ville, latitude, longitude)
    #THEN
    assert isinstance(gare, Gare)
    assert gare.nom == nom


def test_ajout_gare_fail():

    # GIVEN
    id_gare, nom, ville, latitude, longitude = 1, "gare de Rennes", "Rennes", "48,1033° N", "-1,6725° O"
    GareDao().create_gare = MagicMock(return_value=False)
    # WHEN
    gare = GareService().ajout_gare(id_gare, nom, ville, latitude, longitude)
    # THEN
    assert gare is None


def test_recherche_gare():

    # GIVEN
    GareDao.recherche_gare = MagicMock(return_value=gare)
    # WHEN
    resultat = GareService().recherche_gare(id=1)
    # THEN
    assert isinstance(resultat, Gare)
    assert resultat.nom == "gare de Rennes"


def test_supprimer_gare():

    # GIVEN

    # WHEN

    # THEN
