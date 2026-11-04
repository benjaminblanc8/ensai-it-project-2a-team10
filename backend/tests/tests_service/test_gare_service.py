from unittest.mock import MagicMock

from business_object.gare import Gare
from dao.gare_dao import GareDao
from service.gare_service import GareService


gare = Gare(id_gare=9999,
            nom="gare de Rennes",
            ville="Rennes")
 


def test_ajout_gare_ok():

    #GIVEN
    gare_test = Gare(id_gare=None, nom="gare de Rennes", ville="Rennes")
    GareDao.create_gare = MagicMock(return_value=True)
    #WHEN
    gare = GareService().ajout_gare(gare_test)
    #THEN
    assert isinstance(gare, Gare)
    assert gare.nom == nom


def test_ajout_gare_fail():

    # GIVEN
    gare_test = Gare(id_gare=None, nom="gare de Rennes", ville="Rennes")
    GareDao.create_gare = MagicMock(return_value=False)
    # WHEN
    gare = GareService().ajout_gare(gare_test)
    # THEN
    assert gare is None ----


def test_recherche_gare():

    # GIVEN
    GareDao.recherche_gare = MagicMock(return_value=gare)
    # WHEN
    resultat = GareService().recherche_gare(id=9999)
    # THEN
    assert isinstance(resultat, Gare)
    assert resultat.nom == "gare de Rennes"


def test_supprimer_gare_fail():

    #GIVEN
    

def test_supprimer_gare_ok():

    #GIVEN
    GareDao().recherche_gare = MagicMock(return_value=gare)
    #WHEN
    resultat = GareService().supprimer_gare(id=9999)


    #THEN
