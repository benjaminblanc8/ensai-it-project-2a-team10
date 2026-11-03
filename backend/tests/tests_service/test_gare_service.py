import os
from unittest.mock import MagicMock

# Neutralisation totale de la base de données pour faire un vrai test unitaire pur
import dao.db_connection
import pytest
from business_object.gare import Gare
from dao.gare_dao import GareDao
from fastapi import HTTPException
from service.api_sncf_service import ApiSncfService
from service.gare_service import GareService

dao.db_connection.DBConnection = MagicMock()

# Définition d'une clé API factice pour satisfaire l'initialisation de l'API SNCF
os.environ["SNCF_API_KEY"] = "fake_key"


def test_ajout_gare_succes():
    # GIVEN
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    ApiSncfService.recherche_gare_par_nom = MagicMock(return_value=True)
    GareDao.create_gare = MagicMock(return_value=gare)

    # WHEN
    service = GareService()
    resultat = service.ajout_gare(gare)

    # THEN
    assert resultat == gare
    GareDao.create_gare.assert_called_once_with(gare)


def test_ajout_gare_introuvable_sncf():
    # GIVEN
    gare = Gare(id_gare=1, nom="Gare Inconnue", ville="Inconnue")
    ApiSncfService.recherche_gare_par_nom = MagicMock(return_value=False)

    # WHEN / THEN
    service = GareService()
    with pytest.raises(HTTPException) as exc_info:
        service.ajout_gare(gare)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Cette gare n'existe pas."


def test_ajout_gare_echec_dao():
    # GIVEN
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    ApiSncfService.recherche_gare_par_nom = MagicMock(return_value=True)
    GareDao.create_gare = MagicMock(return_value=None)

    # WHEN / THEN
    service = GareService()
    with pytest.raises(HTTPException) as exc_info:
        service.ajout_gare(gare)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Échec de la création de la gare"


def test_recherche_gare_succes():
    # GIVEN
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    GareDao.find_by_id = MagicMock(return_value=gare)

    # WHEN
    service = GareService()
    resultat = service.recherche_gare(1)

    # THEN
    assert resultat == gare
    GareDao.find_by_id.assert_called_once_with(1)


def test_recherche_gare_introuvable():
    # GIVEN
    GareDao.find_by_id = MagicMock(return_value=None)

    # WHEN / THEN
    service = GareService()
    with pytest.raises(HTTPException) as exc_info:
        service.recherche_gare(999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Gare introuvable"


def test_supprimer_gare_succes():
    # GIVEN
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    GareDao.find_by_id = MagicMock(return_value=gare)
    GareDao.supprimer_gare = MagicMock(return_value=True)

    # WHEN
    service = GareService()
    resultat = service.supprimer_gare(1)

    # THEN
    assert resultat == gare
    GareDao.supprimer_gare.assert_called_once_with(1)


def test_supprimer_gare_introuvable():
    # GIVEN
    GareDao.find_by_id = MagicMock(return_value=None)

    # WHEN / THEN
    service = GareService()
    with pytest.raises(HTTPException) as exc_info:
        service.supprimer_gare(999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Gare introuvable"
    