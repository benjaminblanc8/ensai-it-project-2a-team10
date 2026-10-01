from backend.src.business_object.gare import Gare
from backend.src.dao.db_connection import DBConnection


class GareDao:

    def __init__(self):
        """Initialise la connexion à la base de données."""
        self.db = DBConnection()
        self.connection = self.db.connection

    def create_gare(self, gare: Gare) -> bool:
        """Ajoute une gare dans la base de données."""

        requete = """
            INSERT INTO Gare (nom, ville, latitude, longitude)
            VALUES (%s, %s, %s, %s)
            RETURNING id_gare;
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (
                        gare.nom,
                        gare.ville,
                        gare.latitude,
                        gare.longitude
                    )
                )

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
            SELECT id_gare, nom, ville, latitude, longitude
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
            resultat["latitude"],
            resultat["longitude"]
        )

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