from datetime import datetime
from unittest.mock import MagicMock

from business_object.ligne import Ligne
from business_object.trajet import Trajet
from dao.trajet_dao import TrajetDao
from service.trajet_service import TrajetService


def test_recherche_trajet():
    # GIVEN
    trajet_fictif = Trajet(
        id_trajet=1,
        date_heure_depart=datetime(2026, 6, 12, 8, 30),
        duree_minutes=60,
        ligne=None,
        _nb_places=50,
        _tarif=10.0,
        _places_reservees=5
    )

    TrajetDao.rechercher = MagicMock(return_value=trajet_fictif)

    # WHEN
    service = TrajetService()
    resultat = service.recherche_trajet(1)

    # THEN
    assert isinstance(resultat, Trajet)
    assert resultat.id_trajet == 1
    assert resultat.get_places_reservees() == 5


def test_creer_trajet_succes():
    # GIVEN
    ligne = Ligne(id_ligne=1)
    date_depart = datetime(2026, 6, 12, 8, 30)
    TrajetDao.creer_trajet = MagicMock(return_value=True)

    # WHEN
    service = TrajetService()
    resultat = service.creer_trajet(
        ligne=ligne,
        date_heure_depart=date_depart,
        duree_minutes=45,
        nb_places=50,
        tarif=15.0
    )

    # THEN
    assert isinstance(resultat, Trajet)
    assert resultat.duree_minutes == 45
    assert resultat.ligne == ligne
    TrajetDao.creer_trajet.assert_called_once()


def test_creer_trajet_echec():
    # GIVEN
    ligne = Ligne(id_ligne=1)
    date_depart = datetime(2026, 6, 12, 8, 30)
    TrajetDao.creer_trajet = MagicMock(return_value=False)

    # WHEN
    service = TrajetService()
    resultat = service.creer_trajet(
        ligne=ligne,
        date_heure_depart=date_depart,
        duree_minutes=45,
        nb_places=50,
        tarif=15.0
    )

    # THEN
    assert resultat is None
    TrajetDao.creer_trajet.assert_called_once()


def test_supprimer_trajet():
    # GIVEN
    TrajetDao.supprimer_trajet = MagicMock(return_value=True)

    # WHEN
    service = TrajetService()
    resultat = service.supprimer_trajet(1)

    # THEN
    assert resultat is True
    TrajetDao.supprimer_trajet.assert_called_once_with(1)


def test_modifier_trajet():
    # GIVEN
    ligne = Ligne(id_ligne=1)
    date_depart = datetime(2026, 6, 12, 10, 0)
    TrajetDao.modifier_trajet = MagicMock(return_value=True)

    # WHEN
    service = TrajetService()
    resultat = service.modifier_trajet(
        id_trajet=1,
        ligne=ligne,
        date_heure_depart=date_depart,
        duree_minutes=60,
        nb_places=40,
        tarif=12.5,
        places_reservees=5
    )

    # THEN
    assert resultat is True
    TrajetDao.modifier_trajet.assert_called_once()
