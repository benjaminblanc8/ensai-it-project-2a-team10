from business_object.reservation import Reservation
from dao.db_connection import DBConnection
from dao.trajet_dao import TrajetDao
from dao.utilisateur_dao import UtilisateurDao


class ReservationDao:
    """DAO permettant de gérer les réservations des clients."""

    def creer_reservation(self, reservation: Reservation) -> bool:
        """Ajoute une réservation dans la base de données."""

        requete = """
            INSERT INTO Reservation (
                id_utilisateur,
                id_trajet
            )
            VALUES (%s, %s)
            RETURNING id_reservation;
        """

        connexion = DBConnection().connection

        try:
            with connexion.cursor() as cursor:
                cursor.execute(
                    requete,
                    (
                        reservation.utilisateur.id_utilisateur,
                        reservation.trajet.id_trajet,
                    ),
                )

                resultat = cursor.fetchone()

                if resultat is None:
                    raise RuntimeError(
                        "Aucun identifiant retourné après la création."
                    )

                reservation.id_reservation = resultat["id_reservation"]

            connexion.commit()
            return True

        except Exception:
            connexion.rollback()
            raise

    def recherche_reservation(self, id_reservation: int) -> Reservation | None:
        """Recherche une réservation à partir de son identifiant."""

        requete = """
            SELECT id_reservation, id_utilisateur, id_trajet
            FROM Reservation
            WHERE id_reservation = %s;
        """

        with DBConnection().connection.cursor() as cursor:
            cursor.execute(requete, (id_reservation,))
            resultat = cursor.fetchone()

        if resultat is None:
            return None

        utilisateur_dao = UtilisateurDao()
        trajet_dao = TrajetDao()

        utilisateur = utilisateur_dao.recherche_utilisateur(
            resultat["id_utilisateur"]
        )

        trajet = trajet_dao.recherche_trajet(
            resultat["id_trajet"]
        )

        if utilisateur is None or trajet is None:
            return None

        return Reservation(
            resultat["id_reservation"],
            utilisateur,
            trajet,
        )

    def rechercher_reservations_par_utilisateur(
        self,
        id_utilisateur: int,
    ) -> list[Reservation]:
        """Retourne toutes les réservations d'un utilisateur."""

        requete = """
            SELECT id_reservation
            FROM Reservation
            WHERE id_utilisateur = %s
            ORDER BY id_reservation DESC;
        """

        with DBConnection().connection.cursor() as cursor:
            cursor.execute(requete, (id_utilisateur,))
            resultats = cursor.fetchall()

        reservations = []

        for resultat in resultats:
            reservation = self.recherche_reservation(
                resultat["id_reservation"]
            )

            if reservation is not None:
                reservations.append(reservation)

        return reservations

    def supprimer_reservation(
        self,
        id_reservation: int,
        id_utilisateur: int,
    ) -> bool:
        """Annule une réservation appartenant à un utilisateur."""

        requete = """
            DELETE FROM Reservation
            WHERE id_reservation = %s
              AND id_utilisateur = %s;
        """

        connexion = DBConnection().connection

        try:
            with connexion.cursor() as cursor:
                cursor.execute(
                    requete,
                    (id_reservation, id_utilisateur),
                )

                suppression_effectuee = cursor.rowcount > 0

            connexion.commit()
            return suppression_effectuee

        except Exception:
            connexion.rollback()
            raise
