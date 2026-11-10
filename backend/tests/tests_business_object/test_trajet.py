from datetime import datetime
from unittest.mock import MagicMock

from business_object.trajet import Trajet


def test_get_nb_places_disponibles():
    ligne_mock = MagicMock()
    trajet = Trajet(1, datetime(2026, 6, 1, 10, 0), 120, ligne_mock, 50, 35.50, 15)

    assert trajet.get_nb_places_disponibles == 35
    assert trajet.places_restantes() == 35


def test_est_complet():
    ligne_mock = MagicMock()
    trajet_ouvert = Trajet(1, datetime.now(), 60, ligne_mock, 100, 20.0, 40)
    assert trajet_ouvert.est_complet() is False
    trajet_complet = Trajet(2, datetime.now(), 60, ligne_mock, 100, 20.0, 100)
    assert trajet_complet.est_complet() is True


def test_depart_arrivee():
    gare_dep = MagicMock(nom="Rennes")
    gare_arr = MagicMock(nom="Paris")
    ligne_mock = MagicMock(gare_depart=gare_dep, gare_arrivee=gare_arr)

    trajet = Trajet(1, datetime.now(), 90, ligne_mock, 50, 50.0, 10)
    trajet.ligne = ligne_mock

    assert trajet.depart_arrivee() == ("Rennes", "Paris")


def test_get_tarif():
    ligne_mock = MagicMock()
    trajet = Trajet(1, datetime.now(), 60, ligne_mock, 50, 42.99, 0)

    assert trajet.get_tarif == 42.99


def test_get_places_reservees():
    ligne_mock = MagicMock()
    trajet = Trajet(1, datetime(2026, 6, 1, 10, 0), 120, ligne_mock, 50, 35.50, 15)

    assert trajet.get_places_reservees == 15


def test_heure_arrivee():
    ligne_mock = MagicMock()
    trajet = Trajet(1, datetime(2026, 6, 1, 10, 0), 120, ligne_mock, 50, 35.50, 15)

    assert trajet.heure_arrivee() == datetime(2026, 6, 1, 12, 0)


def test_heure_arrivee_sans_duree():
    ligne_mock = MagicMock()
    depart = datetime(2026, 6, 1, 10, 0)
    trajet = Trajet(1, depart, 0, ligne_mock, 50, 35.50, 15)

    assert trajet.heure_arrivee() is None
