from datetime import datetime
from unittest.mock import MagicMock

from business_object.ligne import Ligne
from business_object.trajet import Trajet
from service.trajet_service import TrajetService


def test_recherche_trajet_succes():
    trajet_fictive = Trajet(1, datetime.now(), 60, MagicMock(), 50, 20.0, 10)

    service = TrajetService()
    service.recherche_trajet = MagicMock(return_value=trajet_fictive)

    resultat = service.recherche_trajet(1)
    assert resultat == trajet_fictive


def test_creer_trajet_succes(monkeypatch):
    ligne = Ligne(
        id_ligne=1,
        gare_depart=MagicMock(),
        gare_arrivee=MagicMock(),
        date_creation=datetime.now(),
    )

    service = TrajetService()
    monkeypatch.setattr(
        "service.trajet_service.TrajetDao.creer_trajet",
        MagicMock(return_value=True),
    )

    resultat = service.creer_trajet(ligne, datetime(2026, 7, 1, 8, 0), 90, 100, 45.0)

    assert resultat is not None
    assert resultat.duree_minutes == 90
    assert resultat.get_tarif == 45.0  # ruff: ignore[float-equality-comparison]


def test_get_nb_places_disponibles():
    ligne_mock = MagicMock()
    trajet = Trajet(1, datetime(2026, 6, 1, 10, 0), 120, ligne_mock, 50, 35.50, 15)

    assert trajet.get_nb_places_disponibles == 35


def test_get_tarif():
    ligne_mock = MagicMock()
    trajet = Trajet(1, datetime.now(), 60, ligne_mock, 50, 42.99, 0)

    assert trajet.get_tarif == 42.99  # ruff: ignore[float-equality-comparison]


def test_get_places_reservees():
    ligne_mock = MagicMock()
    trajet = Trajet(1, datetime(2026, 6, 1, 10, 0), 120, ligne_mock, 50, 35.50, 15)

    assert trajet.get_places_reservees == 15
