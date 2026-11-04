import os
from unittest.mock import MagicMock

# Neutralisation totale de la base de données et de l'API SNCF
import dao.db_connection
import pytest
from fastapi import HTTPException

dao.db_connection.DBConnection = MagicMock()
os.environ["SNCF_API_KEY"] = "fake_key"   #  Pour empêcher l'application d'essayer de se connecter à la vraie base de données PostgreSQL ou de réclamer une vraie clé d'API SNCF secrète

from business_object.gare import Gare
from service.api_sncf_service import ApiSncfService
from service.gare_service import GareService


def test_ajout_gare_succes():
    # GIVEN
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    ApiSncfService.gare_existe_par_nom = MagicMock(return_value=True)

    service = GareService()
    service.dao = MagicMock()
    service.dao.creer_gare.return_value = gare

    # WHEN
    resultat = service.ajout_gare(gare)

    # THEN
    assert resultat == gare
    service.dao.creer_gare.assert_called_once_with(gare)


def test_ajout_gare_introuvable_sncf():
    # GIVEN
    gare = Gare(id_gare=1, nom="Gare Inconnue", ville="Inconnue")
    ApiSncfService.gare_existe_par_nom = MagicMock(return_value=False)

    # WHEN / THEN
    service = GareService()
    with pytest.raises(HTTPException) as exc_info:
        service.ajout_gare(gare)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Cette gare n'existe pas."


def test_ajout_gare_echec_dao():
    # GIVEN
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    ApiSncfService.gare_existe_par_nom = MagicMock(return_value=True)

    service = GareService()
    service.dao = MagicMock()
    service.dao.creer_gare.return_value = None

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc_info:
        service.ajout_gare(gare)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Échec de la création de la gare"


def test_recherche_gare_succes():
    # GIVEN
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    
    service = GareService()
    service.dao = MagicMock()
    service.dao.recherche_gare.return_value = gare

    # WHEN
    resultat = service.recherche_gare(1)

    # THEN
    assert resultat == gare
    service.dao.recherche_gare.assert_called_once_with(1)


def test_recherche_gare_introuvable():
    # GIVEN
    service = GareService()
    service.dao = MagicMock()
    service.dao.recherche_gare.return_value = None

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc_info:
        service.recherche_gare(999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Gare introuvable"


def test_supprimer_gare_succes():
    # GIVEN
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    
    service = GareService()
    service.dao = MagicMock()
    service.dao.recherche_gare.return_value = gare
    service.dao.supprimer_gare.return_value = True

    # WHEN
    resultat = service.supprimer_gare(1)

    # THEN
    assert resultat == gare
    service.dao.supprimer_gare.assert_called_once_with(1)


def test_supprimer_gare_introuvable():
    # GIVEN
    service = GareService()
    service.dao = MagicMock()
    service.dao.recherche_gare.return_value = None

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc_info:
        service.supprimer_gare(999)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Gare introuvable"