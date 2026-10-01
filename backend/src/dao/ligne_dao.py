from src.business_object.ligne import Ligne
from src.dao.db_connection import DBConnection
from src.dao.gare_dao import GareDao


class LigneDao:

    def create_ligne(self, ligne: Ligne) -> bool:
        """Ajoute une ligne dans la base de données."""

        requete = """
            INSERT INTO Ligne (
                libelle,
                id_gare_depart,
                id_gare_arrivee,
                date_creation
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id_ligne;
        """

        try:
            with DBConnection().connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (
                        ligne.libelle,
                        ligne.gare_depart.id_gare,
                        ligne.gare_arrivee.id_gare,
                        ligne.date_creation
                    )
                )

                resultat = cursor.fetchone()
                ligne.id_ligne = resultat["id_ligne"]

            DBConnection().connection.commit()
            return True

        except Exception:
            DBConnection().connection.rollback()
            raise

    def modifier_ligne(self, ligne: Ligne) -> bool:
        """Modifie une ligne existante."""

        requete = """
            UPDATE Ligne
            SET libelle = %s,
                id_gare_depart = %s,
                id_gare_arrivee = %s,
                date_creation = %s
            WHERE id_ligne = %s;
        """

        try:
            with DBConnection().connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (
                        ligne.libelle,
                        ligne.gare_depart.id_gare,
                        ligne.gare_arrivee.id_gare,
                        ligne.date_creation,
                        ligne.id_ligne
                    )
                )

                modification_effectuee = cursor.rowcount > 0

            DBConnection().connection.commit()
            return modification_effectuee

        except Exception:
            DBConnection().connection.rollback()
            raise

    def supprimer_ligne(self, ligne: Ligne) -> bool:
        """Supprime une ligne."""

        requete = """
            DELETE FROM Ligne
            WHERE id_ligne = %s;
        """

        try:
            with DBConnection().connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (ligne.id_ligne,)
                )

                suppression_effectuee = cursor.rowcount > 0

            DBConnection().connection.commit()
            return suppression_effectuee

        except Exception:
            DBConnection().connection.rollback()
            raise

    def recherche_ligne(self, id_ligne: int) -> Ligne | None:
        """Recherche une ligne à partir de son identifiant."""

        requete = """
            SELECT
                id_ligne,
                libelle,
                id_gare_depart,
                id_gare_arrivee,
                date_creation
            FROM Ligne
            WHERE id_ligne = %s;
        """

        with DBConnection().connection.cursor() as cursor:
            cursor.execute(requete, (id_ligne,))
            resultat = cursor.fetchone()

        if resultat is None:
            return None

        gare_dao = GareDao()

        gare_depart = gare_dao.recherche_gare(
            resultat["id_gare_depart"]
        )

        gare_arrivee = gare_dao.recherche_gare(
            resultat["id_gare_arrivee"]
        )

        return Ligne(
            resultat["id_ligne"],
            resultat["libelle"],
            gare_depart,
            gare_arrivee,
            resultat["date_creation"]
        )