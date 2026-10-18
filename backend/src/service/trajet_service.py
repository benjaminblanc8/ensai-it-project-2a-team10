
import datetime

from business_object.ligne import Ligne
from business_object.trajet import Trajet
from dao.trajet_dao import TrajetDao


class TrajetService:
    def recherche_trajet(self, id_trajet: int):
        """Recherche un trajet par son ID.

        Returns:
            Le trajet correspondant, ou None s'il n'existe pas.
        """
        return TrajetDao().rechercher(id_trajet)

    def creer_trajet(
        self,
        ligne: Ligne,
        date_heure_depart: datetime.datetime,
        duree_minutes: int,
        nb_places: int,
        tarif: float,
    ):
        """Crée un nouveau trajet.

        Returns:
            Le trajet créé, ou None si la création échoue.
        """
        nouveau_trajet = Trajet(
            id_trajet=None,
            date_heure_depart=date_heure_depart,
            duree_minutes=duree_minutes,
            ligne=ligne,
            _nb_places=nb_places,
            _tarif=tarif,
        )

        return (
            nouveau_trajet
            if TrajetDao().creer_trajet(nouveau_trajet)
            else None
        )

    def supprimer_trajet(self, id_trajet: int):
        """Supprime un trajet.

        Returns:
            True si la suppression réussit, False sinon.
        """
        return TrajetDao().supprimer_trajet(id_trajet)

    def modifier_trajet(
        self,
        id_trajet: int,
        ligne: Ligne,
        date_heure_depart: datetime.datetime,
        duree_minutes: int,
        nb_places: int,
        tarif: float,
        places_reservees: int,
    ):
        """Modifie un trajet existant.

        Returns:
            True si la modification réussit, False sinon.
        """
        trajet = Trajet(
            id_trajet=id_trajet,
            date_heure_depart=date_heure_depart,
            duree_minutes=duree_minutes,
            ligne=ligne,
            _nb_places=nb_places,
            _tarif=tarif,
            _places_reservees=places_reservees,
        )

        return TrajetDao().modifier_trajet(trajet)
