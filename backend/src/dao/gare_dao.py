from business_object.gare import Gare
from dao.db_connection import DBConnection


class GareDao:
    def __init__(self):
        """Initialise la connexion à la base de données."""
        self.db = DBConnection()
        self.connection = self.db.connection

    def creer_gare(self, gare: Gare) -> bool:
        """Ajoute une gare dans la base de données."""

        requete = """
            INSERT INTO Gare (nom, ville, id_gare_sncf)
            VALUES (%s, %s, %s)
            RETURNING id_gare;
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(requete, (gare.nom, gare.ville, gare.id_gare_sncf))

                resultat = cursor.fetchone()

                # On récupère l'id généré par PostgreSQL
                gare.id_gare = resultat["id_gare"]

            self.connection.commit()
            return True

        except Exception:
            self.connection.rollback()
            raise

    def recherche_gare(self, id_gare: int) -> Gare | None:
        """Recherche une gare à partir de son identifiant."""

        requete = """
            SELECT id_gare, nom, ville, id_gare_sncf
            FROM Gare
            WHERE id_gare = %s;
        """

        with self.connection.cursor() as cursor:
            cursor.execute(requete, (id_gare,))
            resultat = cursor.fetchone()

        if resultat is None:
            return None

        return Gare(
            resultat["id_gare"],
            resultat["nom"],
            resultat["ville"],
            resultat["id_gare_sncf"],
        )

    def recherche_gare_par_nom(self, nom: str) -> list[Gare]:
        """Recherche toutes les gares dont le nom contient la chaîne fournie."""

        requete = """
            SELECT id_gare, nom, ville, id_gare_sncf
            FROM Gare
            WHERE nom ILIKE %s;
        """

        with self.connection.cursor() as cursor:
            cursor.execute(requete, (f"%{nom}%",))
            resultats = cursor.fetchall()

        return [
            Gare(
                resultat["id_gare"],
                resultat["nom"],
                resultat["ville"],
                resultat["id_gare_sncf"],
            )
            for resultat in resultats
        ]

    def supprimer_gare(self, id_gare: int) -> bool:
        """Supprime une gare à partir de son identifiant."""

        requete = """
            DELETE FROM Gare
            WHERE id_gare = %s;
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(requete, (id_gare,))

                suppression_effectuee = cursor.rowcount > 0

            self.connection.commit()
            return suppression_effectuee

        except Exception:
            self.connection.rollback()
            raise
