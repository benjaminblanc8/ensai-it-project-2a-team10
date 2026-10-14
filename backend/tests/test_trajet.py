from datetime import datetime
from unittest.mock import MagicMock
from backend.src.business_object.trajet import Trajet


def test_get_nb_places_disponibles():
    ligne_mock = MagicMock()
    trajet = Trajet(
        id_trajet=1,
        date_heure_depart=datetime(2026, 6, 1, 10, 0),
        duree_minutes=120,
        ligne=ligne_mock,
        _nb_places=50,
        _tarif=35.50,
        _places_reservees=15
    )

    assert trajet.get_nb_places_disponibles() == 35
    assert trajet.places_restantes() == 35


def test_est_complet():
    ligne_mock = MagicMock()

    trajet_ouvert = Trajet(1, datetime.now(), 60, ligne_mock, 100, 20.0, 40) # cas où le trajet n'est pas complet
    assert trajet_ouvert.est_complet() is False

    trajet_complet = Trajet(2, datetime.now(), 60, ligne_mock, 100, 20.0, 100) # cas où le trajet est complet
    assert trajet_complet.est_complet() is True



def test_depart_arrivee():
    gare_dep = MagicMock(nom="Rennes")
    gare_arr = MagicMock(nom="Paris")
    ligne_mock = MagicMock(gare_depart=gare_dep, gare_arrivee=gare_arr)

    trajet = Trajet(1, datetime.now(), 90, ligne_mock, 50, 50.0, 10)

    assert trajet.depart_arrivee() == ("Rennes", "Paris")


def test_get_tarif():
    ligne_mock = MagicMock()
    trajet = Trajet(1, datetime.now(), 60, ligne_mock, 50, 42.99, 0)

    assert trajet.get_tarif() == 42.99