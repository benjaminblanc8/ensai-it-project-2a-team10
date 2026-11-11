import os
from datetime import datetime
from unittest.mock import MagicMock

import dao.db_connection
import pytest
from business_object.ligne import Ligne
from business_object.niveau_habilitation import NiveauHabilitation
from business_object.trajet import Trajet
from business_object.utilisateur import Utilisateur
from service.reservation_service import ReservationService

dao.db_connection.DBConnection = MagicMock()
os.environ["SNCF_API_KEY"] = "fake_key"


def _fabrique_trajet(
    places: int = 10,
    reservees: int = 0,
) -> Trajet:
    ligne = Ligne(
        id_ligne=1,
        gare_depart=MagicMock(),
        gare_arrivee=MagicMock(),
        date_creation=datetime.now(),
    )
    return Trajet(
        id_trajet=1,
        date_heure_depart=datetime.now(),
        duree_minutes=60,
        ligne=ligne,
        _nb_places=places,
        _tarif=50.0,
        _places_reservees=reservees,
    )


def _fabrique_utilisateur(id: int = 1) -> Utilisateur:
    return Utilisateur(
        id_utilisateur=id,
        pseudo=f"test{id}",
        mdp="fake_hashed_pwd",
        niveau=NiveauHabilitation.CLIENT,
    )


# --- creer_reservation ---


def test_creer_reservation_trajet_introuvable():
    utilisateur = _fabrique_utilisateur()

    trajet_dao = MagicMock()
    trajet_dao.recherche_trajet.return_value = None

    reservation_dao = MagicMock()

    service = ReservationService(reservation_dao, trajet_dao)
    with pytest.raises(LookupError):
        service.creer_reservation(utilisateur, 999)


def test_creer_reservation_complet():
    trajet = _fabrique_trajet(places=10, reservees=10)
    utilisateur = _fabrique_utilisateur()

    trajet_dao = MagicMock()
    trajet_dao.recherche_trajet.return_value = trajet

    reservation_dao = MagicMock()

    service = ReservationService(reservation_dao, trajet_dao)
    with pytest.raises(ValueError):
        service.creer_reservation(utilisateur, 1)

    reservation_dao.creer_reservation.assert_not_called()


def test_creer_reservation_echec_dao():
    trajet = _fabrique_trajet(places=10, reservees=0)
    utilisateur = _fabrique_utilisateur()

    trajet_dao = MagicMock()
    trajet_dao.recherche_trajet.return_value = trajet

    reservation_dao = MagicMock()
    reservation_dao.creer_reservation.return_value = False

    service = ReservationService(reservation_dao, trajet_dao)
    with pytest.raises(RuntimeError):
        service.creer_reservation(utilisateur, 1)

    trajet_dao.incrementer_places_reservees.assert_not_called()

# --- annuler_reservation ---


def test_annuler_reservation_introuvable():
    utilisateur = _fabrique_utilisateur()

    reservation_dao = MagicMock()
    reservation_dao.recherche_reservation.return_value = None

    trajet_dao = MagicMock()

    service = ReservationService(reservation_dao, trajet_dao)
    with pytest.raises(LookupError):
        service.annuler_reservation(utilisateur, 999)


def test_annuler_reservation_autre_utilisateur():
    proprietaire = _fabrique_utilisateur(id=1)
    intrus = _fabrique_utilisateur(id=2)

    reservation = MagicMock()
    reservation.utilisateur = proprietaire

    reservation_dao = MagicMock()
    reservation_dao.recherche_reservation.return_value = reservation

    trajet_dao = MagicMock()

    service = ReservationService(reservation_dao, trajet_dao)
    with pytest.raises(PermissionError):
        service.annuler_reservation(intrus, 42)

    reservation_dao.supprimer_reservation.assert_not_called()


def test_annuler_reservation_echec_dao():
    utilisateur = _fabrique_utilisateur()
    trajet = _fabrique_trajet()

    reservation = MagicMock()
    reservation.utilisateur = utilisateur
    reservation.trajet = trajet

    reservation_dao = MagicMock()
    reservation_dao.recherche_reservation.return_value = reservation
    reservation_dao.supprimer_reservation.return_value = False

    trajet_dao = MagicMock()

    service = ReservationService(reservation_dao, trajet_dao)
    with pytest.raises(RuntimeError):
        service.annuler_reservation(utilisateur, 42)

    trajet_dao.decrementer_places_reservees.assert_not_called()
