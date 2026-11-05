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
        """Réserve une place sur un trajet pour un client."""

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

        return reservation

    def rechercher_reservations(
        self,
        utilisateur: Utilisateur,
    ) -> list[Reservation]:
        """Retourne toutes les réservations du client."""

        return self.reservation_dao.rechercher_reservations_par_utilisateur(
            utilisateur.id_utilisateur
        )

    def annuler_reservation(
        self,
        utilisateur: Utilisateur,
        id_reservation: int,
    ) -> bool:
        """Annule une réservation appartenant au client."""

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

        return True