import os
from datetime import datetime
from unittest.mock import MagicMock

import dao.db_connection
import pytest
from business_object.gare import Gare
from business_object.ligne import Ligne
from fastapi import HTTPException
from service.gare_service import GareService
from service.ligne_service import LigneService

dao.db_connection.DBConnection = MagicMock()
os.environ["SNCF_API_KEY"] = "fake_key"


def test_creer_ligne_succes(monkeypatch):
    gare_depart = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    gare_arrivee = Gare(id_gare=2, nom="Paris", ville="Paris")

    monkeypatch.setattr(GareService, "recherche_gare", MagicMock(side_effect=[gare_depart, gare_arrivee]))

    service = LigneService()
    service.dao = MagicMock()
    service.dao.rechercher_ids_par_gares.return_value = []
    service.dao.creer_ligne.return_value = True

    resultat = service.creer(gare_depart, gare_arrivee)

    assert isinstance(resultat, Ligne)
    assert resultat.gare_depart == gare_depart
    assert resultat.gare_arrivee == gare_arrivee
    service.dao.creer_ligne.assert_called_once()


def test_creer_ligne_gares_identiques(monkeypatch):
    gare_depart = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    monkeypatch.setattr(GareService, "recherche_gare", MagicMock(return_value=gare_depart))

    service = LigneService()
    with pytest.raises(HTTPException) as exc_info:
        service.creer(gare_depart, gare_depart)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Les gares de départ et d'arrivée doivent être différentes."


def test_creer_ligne_echec_dao(monkeypatch):
    gare_depart = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    gare_arrivee = Gare(id_gare=2, nom="Paris", ville="Paris")
    monkeypatch.setattr(GareService, "recherche_gare", MagicMock(side_effect=[gare_depart, gare_arrivee]))

    service = LigneService()
    service.dao = MagicMock()
    service.dao.rechercher_ids_par_gares.return_value = []
    service.dao.creer_ligne.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        service.creer(gare_depart, gare_arrivee)

    assert exc_info.value.status_code == 500


def test_rechercher_ligne_succes():
    ligne_fictive = Ligne(id_ligne=1, gare_depart=MagicMock(), gare_arrivee=MagicMock(), date_creation=datetime.now())

    service = LigneService()
    service.dao = MagicMock()
    service.dao.recherche_ligne.return_value = ligne_fictive

    resultat = service.rechercher_ligne(1)

    assert resultat == ligne_fictive
    service.dao.recherche_ligne.assert_called_once_with(1)


def test_supprimer_ligne_succes():
    service = LigneService()
    service.dao = MagicMock()
    service.dao.supprimer_ligne.return_value = True

    resultat = service.supprimer_ligne(1)

    assert resultat is True
    service.dao.supprimer_ligne.assert_called_once_with(1)


def test_modifier_ligne_succes():
    ligne = Ligne(id_ligne=1, gare_depart=MagicMock(), gare_arrivee=MagicMock(), date_creation=datetime.now())

    service = LigneService()
    service.dao = MagicMock()
    service.dao.recherche_ligne.return_value = ligne
    service.dao.rechercher_ids_par_gares.return_value = []
    service.dao.modifier_ligne.return_value = True

    gare_dep = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    gare_arr = Gare(id_gare=2, nom="Paris", ville="Paris")
    service.gare_service = MagicMock()
    service.gare_service.recherche_gare.side_effect = [gare_dep, gare_arr]

    resultat = service.modifier_ligne(1, gare_dep, gare_arr)

    assert resultat is True
    service.dao.modifier_ligne.assert_called_once()
