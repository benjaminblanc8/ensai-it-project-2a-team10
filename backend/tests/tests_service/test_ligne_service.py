import os
from datetime import datetime
from unittest.mock import MagicMock

# Neutralisation totale de la base de données
import dao.db_connection
import pytest
from business_object.gare import Gare
from business_object.ligne import Ligne
from dao.ligne_dao import LigneDao
from fastapi import HTTPException
from service.gare_service import GareService
from service.ligne_service import LigneService

dao.db_connection.DBConnection = MagicMock()

# Définition d'une clé API factice
os.environ["SNCF_API_KEY"] = "fake_key"


def test_creer_ligne_succes():
    # GIVEN
    gare_depart = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    gare_arrivee = Gare(id_gare=2, nom="Paris", ville="Paris")
    GareService.recherche_gare = MagicMock(side_effect=[gare_depart, gare_arrivee])
    LigneDao.creer = MagicMock(return_value=True)

    # WHEN
    service = LigneService()
    resultat = service.creer(gare_depart, gare_arrivee)

    # THEN
    assert isinstance(resultat, Ligne)
    assert resultat.gare_depart == gare_depart
    assert resultat.gare_arrivee == gare_arrivee
    LigneDao.creer.assert_called_once()


def test_creer_ligne_gares_identiques():
    # GIVEN
    gare_depart = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    gare_arrivee = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    GareService.recherche_gare = MagicMock(return_value=gare_depart)

    # WHEN / THEN
    service = LigneService()
    with pytest.raises(HTTPException) as exc_info:
        service.creer(gare_depart, gare_arrivee)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Les gares de départ et d'arrivée doivent être différentes."


def test_creer_ligne_echec_dao():
    # GIVEN
    gare_depart = Gare(id_gare=1, nom="Rennes", ville="Rennes")
    gare_arrivee = Gare(id_gare=2, nom="Paris", ville="Paris")
    GareService.recherche_gare = MagicMock(side_effect=[gare_depart, gare_arrivee])
    LigneDao.creer = MagicMock(return_value=False)

    # WHEN / THEN
    service = LigneService()
    with pytest.raises(HTTPException) as exc_info:
        service.creer(gare_depart, gare_arrivee)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Échec de la création de la ligne."


def test_rechercher_ligne_succes():
    # GIVEN
    ligne_fictive = Ligne(
        id_ligne=1,
        gare_depart=MagicMock(),
        gare_arrivee=MagicMock(),
        date_creation=datetime.now()
    )
    LigneDao.rechercher = MagicMock(return_value=ligne_fictive)

    # WHEN
    service = LigneService()
    resultat = service.rechercher_ligne(1)

    # THEN
    assert resultat == ligne_fictive
    LigneDao.rechercher.assert_called_once_with(1)


def test_supprimer_ligne_succes():
    # GIVEN
    LigneDao.delete = MagicMock(return_value=True)

    # WHEN
    service = LigneService()
    resultat = service.supprimer_ligne(1)

    # THEN
    assert resultat is True
    LigneDao.delete.assert_called_once_with(1)


def test_modifier_ligne_succes():
    # GIVEN
    ligne = Ligne(
        id_ligne=1,
        gare_depart=MagicMock(),
        gare_arrivee=MagicMock(),
        date_creation=datetime.now()
    )
    LigneDao.modifier = MagicMock(return_value=True)

    # WHEN
    service = LigneService()
    resultat = service.modifier_ligne(ligne, gare_depart=MagicMock(), gare_arrivee=MagicMock())

    # THEN
    assert resultat is True
    LigneDao.modifier.assert_called_once_with(ligne)
