import datetime

from business_object.gare import Gare
from business_object.ligne import Ligne
from business_object.trajet import Trajet
from dao.trajet_dao import TrajetDao


class TrajetService:
    def recherche_trajet(self, id_trajet: int):
        """Recherche un trajet par son ID
        Args:
            id_trajet: int
        Returns:
            l'objet Trajet correspondant à l'ID ou "None" si le trajet n'existe pas
        """
        return TrajetDao().rechercher(id_trajet)

    def creer_trajet(
        self,
        ligne: Ligne,
        date_heure_depart: datetime,
        duree_minutes: int,
        gare_depart: Gare,
        gare_arrivee: Gare,
        nb_places: int,
        tarif: float,
    ):
        """Création d'un nouveau trajet
        Args:
            ligne: Ligne
            date_heure_depart: datetime
            duree_minutes: int
            gare_depart: Gare
            gare_arrivee: Gare
            nb_places: int
            tarif: float
        Returns:
            l'objet Trajet est créé ou "None" si la création a échoué
        """
        nouveau_trajet = Trajet(
            id_trajet=None,
            ligne=ligne,
            date_heure_depart=date_heure_depart,
            duree_minutes=duree_minutes,
            gare_depart=gare_depart,
            gare_arrivee=gare_arrivee,
            nb_places=nb_places,
            tarif=tarif,
        )

        return nouveau_trajet if TrajetDao().creer_trajet(nouveau_trajet) else None

    def supprimer_trajet(self, id_trajet: int):
        """Supprime un trajet existant
        Args:
            id_trajet: int
        Returns:
            True si la suppression a réussi, False sinon
        """
        return TrajetDao().supprimer_trajet(id_trajet)

    def modifier_trajet(
        self,
        id_trajet: int,
        ligne: Ligne,
        date_heure_depart: datetime,
        duree_minutes: int,
        gare_depart: Gare,
        gare_arrivee: Gare,
        nb_places: int,
        tarif: float,
        places_reservees: int,
    ):
        """Modifie un trajet existant
        Args:
            id_trajet: int
            ligne: Ligne
            date_heure_depart: datetime
            duree_minutes: int
            gare_depart: Gare
            gare_arrivee: Gare
        Returns:
            True si la modification a réussi, False sinon
        """
        trajet = Trajet(
            id_trajet=id_trajet,
            ligne=ligne,
            date_heure_depart=date_heure_depart,
            duree_minutes=duree_minutes,
            gare_depart=gare_depart,
            gare_arrivee=gare_arrivee,
            nb_places=nb_places,
            tarif=tarif,
            places_reservees=places_reservees,
        )

        return TrajetDao().modifier_trajet(trajet)
