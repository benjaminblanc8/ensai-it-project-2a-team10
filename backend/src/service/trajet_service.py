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
        return TrajetDao().recherche_trajet(id_trajet)

    def creer_trajet(
        self,
        ligne: Ligne,
        date_heure_depart: datetime.datetime,
        duree_minutes: int,
        nb_places: int,
        tarif: float,
    ):
        """Crée un nouveau trajet.

        Parameters
        ----------
        ligne : Ligne
            La ligne associée au trajet.
        date_heure_depart : datetime.datetime
            La date et l'heure de départ du trajet.
        duree_minutes : int
            La durée du trajet en minutes.

        Returns
        -------
        Trajet | None
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

        return nouveau_trajet if TrajetDao().creer_trajet(nouveau_trajet) else None

    def supprimer_trajet(self, id_trajet: int):
        """Supprime un trajet.

        Parameters
        ----------
        id_trajet : int
            L'identifiant du trajet à supprimer.

        Returns
        -------
        bool
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

        Parameters
        ----------
        id_trajet : int
            L'identifiant du trajet à modifier.
        ligne : Ligne
            La ligne associée au trajet.
        date_heure_depart : datetime.datetime
            La date et l'heure de départ du trajet.
        duree_minutes : int
            La durée du trajet en minutes.
        nb_places : int
            Le nombre de places disponibles sur le trajet.
        tarif : float
            Le tarif du trajet.
        places_reservees : int
            Le nombre de places déjà réservées sur le trajet.

        Returns
        -------
        bool
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

    def rechercher_trajets_par_ligne(self, ligne: Ligne) -> list[Trajet]:
        """Retourne tous les trajets associés à une ligne donnée.

        Parameters
        ----------
        ligne : Ligne
            La ligne pour laquelle rechercher les trajets.

        Returns
        -------
        list[Trajet]
            La liste des trajets associés à la ligne.
        """

        return TrajetDao().rechercher_trajets_par_ligne(ligne)
