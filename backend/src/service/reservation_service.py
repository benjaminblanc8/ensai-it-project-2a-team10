from business_object.reservation import Reservation
from business_object.utilisateur import Utilisateur
from dao.reservation_dao import ReservationDao
from dao.trajet_dao import TrajetDao


class ReservationService:
    """Gère les réservations des clients."""

    def __init__(
        self,
        reservation_dao: ReservationDao,
        trajet_dao: TrajetDao,
    ):
        self.reservation_dao = reservation_dao
        self.trajet_dao = trajet_dao

    def creer_reservation(
        self,
        utilisateur: Utilisateur,
        id_trajet: int,
    ) -> Reservation:
        """Réserve une place sur un trajet pour un client.

        Parameters
        ----------
        utilisateur : Utilisateur
            L'utilisateur qui effectue la réservation.
        id_trajet : int
            L'identifiant du trajet sur lequel réserver.

        Returns
        -------
        Reservation
            La réservation créée.

        Raises
        --------
        LookupError: Si le trajet n'est pas trouvé.
        ValueError: Si aucune place n'est disponible sur le trajet.
        RuntimeError: Si la création de la réservation échoue.
        """

        trajet = self.trajet_dao.recherche_trajet(id_trajet)

        if trajet is None:
            raise LookupError("Trajet introuvable.")

        places_disponibles = trajet.get_nb_places_disponibles

        if places_disponibles <= 0:
            raise ValueError(
                "Impossible de réserver : aucune place disponible sur ce trajet."
            )

        reservation = Reservation(
            None,
            utilisateur,
            trajet,
        )

        reservation_creee = self.reservation_dao.creer_reservation(reservation)

        if not reservation_creee:
            raise RuntimeError("La création de la réservation a échoué.")

        self.trajet_dao.incrementer_places_reservees(id_trajet)

        return reservation

    def rechercher_reservations(
        self,
        utilisateur: Utilisateur,
    ) -> list[Reservation]:
        """Retourne toutes les réservations du client.

        Parameters
        ----------
        utilisateur : Utilisateur
            L'utilisateur dont on veut récupérer les réservations.

        Returns
        -------
        list[Reservation]
            La liste des réservations du client.

        Raises
        ------
        LookupError: Si aucune réservation n'est trouvée pour l'utilisateur.
        """

        return self.reservation_dao.rechercher_reservations_par_utilisateur(
            utilisateur.id_utilisateur
        )

    def annuler_reservation(
        self,
        utilisateur: Utilisateur,
        id_reservation: int,
    ) -> bool:
        """Annule une réservation appartenant au client.

        Parameters
        ----------
        utilisateur : Utilisateur
            L'utilisateur qui souhaite annuler la réservation.
        id_reservation : int
            L'identifiant de la réservation à annuler.

        Returns
        -------
        bool
            True si l'annulation est réussie, False sinon.

        Raises
        --------
        LookupError: Si la réservation n'est pas trouvée.
        PermissionError: Si l'utilisateur n'est pas le propriétaire de la réservation.
        RuntimeError: Si l'annulation de la réservation échoue.
        """

        reservation = self.reservation_dao.recherche_reservation(id_reservation)

        if reservation is None:
            raise LookupError("Réservation introuvable.")

        if reservation.utilisateur.id_utilisateur != utilisateur.id_utilisateur:
            raise PermissionError(
                "Vous ne pouvez pas annuler la réservation d'un autre client."
            )

        suppression_effectuee = self.reservation_dao.supprimer_reservation(
            id_reservation,
            utilisateur.id_utilisateur,
        )

        if not suppression_effectuee:
            raise RuntimeError("L'annulation de la réservation a échoué.")

        self.trajet_dao.decrementer_places_reservees(reservation.trajet.id_trajet)

        return True
