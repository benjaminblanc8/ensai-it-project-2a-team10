import os
from unittest.mock import MagicMock

import dao.db_connection
import pytest
from business_object.gare import Gare
from fastapi import HTTPException
from service.gare_service import GareService

dao.db_connection.DBConnection = MagicMock()
os.environ["SNCF_API_KEY"] = "fake_key"


def test_ajout_gare_succes():
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")

    service = GareService()
    service.api_sncf_service = MagicMock()
    service.api_sncf_service.obtenir_arrets_par_nom.return_value = [
        {"id_gare_sncf": "STOP:123", "nom": "Rennes"}
    ]
    service.dao = MagicMock()
    service.dao.creer_gare.return_value = True

    resultat = service.ajout_gare(gare)

    assert resultat == gare
    service.dao.creer_gare.assert_called_once_with(gare)


def test_ajout_gare_introuvable_sncf():
    gare = Gare(id_gare=1, nom="Gare Inconnue", ville="Inconnue")

    service = GareService()
    service.api_sncf_service = MagicMock()
    service.api_sncf_service.obtenir_arrets_par_nom.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        service.ajout_gare(gare)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Aucune gare SNCF ne correspond à ce nom."


def test_ajout_gare_echec_dao():
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")

    service = GareService()
    service.api_sncf_service = MagicMock()
    service.api_sncf_service.obtenir_arrets_par_nom.return_value = [
        {"id_gare_sncf": "STOP:123", "nom": "Rennes"}
    ]
    service.dao = MagicMock()
    service.dao.creer_gare.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        service.ajout_gare(gare)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Échec de la création de la gare."


def test_recherche_gare_succes():
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")

    service = GareService()
    service.dao = MagicMock()
    service.dao.recherche_gare.return_value = gare

    resultat = service.recherche_gare(1)

    assert resultat == gare
    service.dao.recherche_gare.assert_called_once_with(1)


def test_recherche_gare_introuvable():
    service = GareService()
    service.dao = MagicMock()
    service.dao.recherche_gare.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.recherche_gare(999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Gare introuvable"


def test_supprimer_gare_succes():
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes")

    service = GareService()
    service.dao = MagicMock()
    service.dao.recherche_gare.return_value = gare
    service.dao.supprimer_gare.return_value = True

    resultat = service.supprimer_gare(1)

    assert resultat == gare
    service.dao.supprimer_gare.assert_called_once_with(1)


def test_supprimer_gare_introuvable():
    service = GareService()
    service.dao = MagicMock()
    service.dao.recherche_gare.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.supprimer_gare(999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Gare introuvable"
