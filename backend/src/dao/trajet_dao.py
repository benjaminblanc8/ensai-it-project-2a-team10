from src.business_object.trajet import Trajet
from src.dao.db_connection import DBConnection
from src.dao.ligne_dao import LigneDao


class TrajetDao:

    def create_trajet(self, trajet: Trajet) -> bool:
        """Ajoute un trajet dans la base de données."""

        requete = """
            INSERT INTO Trajet (
                date_heure_depart,
                duree_minutes,
                id_ligne,
                nb_places,
                tarif,
                places_reservees
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_trajet;
        """

        try:
            with DBConnection().connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (
                        trajet.date_heure_depart,
                        trajet.duree_minutes,
                        trajet.ligne.id_ligne,
                        trajet._nb_places,
                        trajet.get_tarif(),
                        trajet.get_places_reservees()
                    )
                )

                resultat = cursor.fetchone()
                trajet.id_trajet = resultat["id_trajet"]

            DBConnection().connection.commit()
            return True

        except Exception:
            DBConnection().connection.rollback()
            raise

    def recherche_trajet(self, id_trajet: int) -> Trajet | None:
        """Recherche un trajet à partir de son identifiant."""

        requete = """
            SELECT
                id_trajet,
                date_heure_depart,
                duree_minutes,
                id_ligne,
                nb_places,
                tarif,
                places_reservees
            FROM Trajet
            WHERE id_trajet = %s;
        """

        with DBConnection().connection.cursor() as cursor:
            cursor.execute(requete, (id_trajet,))
            resultat = cursor.fetchone()

        if resultat is None:
            return None

        ligne = LigneDao().recherche_ligne(
            resultat["id_ligne"]
        )

        return Trajet(
            resultat["id_trajet"],
            resultat["date_heure_depart"],
            resultat["duree_minutes"],
            ligne,
            resultat["nb_places"],
            float(resultat["tarif"]),
            resultat["places_reservees"]
        )

    def supprimer_trajet(self, trajet: Trajet) -> bool:
        """Supprime un trajet."""

        requete = """
            DELETE FROM Trajet
            WHERE id_trajet = %s;
        """

        try:
            with DBConnection().connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (trajet.id_trajet,)
                )

                suppression_effectuee = cursor.rowcount > 0

            DBConnection().connection.commit()
            return suppression_effectuee

        except Exception:
            DBConnection().connection.rollback()
            raise

    def modifier_trajet(self, trajet: Trajet) -> bool:
        """Modifie les informations d'un trajet."""

        requete = """
            UPDATE Trajet
            SET date_heure_depart = %s,
                duree_minutes = %s,
                id_ligne = %s,
                nb_places = %s,
                tarif = %s,
                places_reservees = %s
            WHERE id_trajet = %s;
        """

        try:
            with DBConnection().connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (
                        trajet.date_heure_depart,
                        trajet.duree_minutes,
                        trajet.ligne.id_ligne,
                        trajet._nb_places,
                        trajet.get_tarif(),
                        trajet.get_places_reservees(),
                        trajet.id_trajet
                    )
                )

                modification_effectuee = cursor.rowcount > 0

            DBConnection().connection.commit()
            return modification_effectuee

        except Exception:
            DBConnection().connection.rollback()
            raise