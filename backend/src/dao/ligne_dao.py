import psycopg2
from business_object.gare import Gare
from business_object.ligne import Ligne
from dao.db_connection import DBConnection
from dao.gare_dao import GareDao


class LigneDao:
    def creer_ligne(self, ligne: Ligne) -> bool:
        """Ajoute une ligne dans la base de données."""

        requete = """
            INSERT INTO Ligne (
                id_gare_depart,
                id_gare_arrivee,
                date_creation
            )
            VALUES (%s, %s, %s)
            RETURNING id_ligne;
        """

        db = DBConnection()
        connection = db.connection

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (
                        ligne.gare_depart.id_gare,
                        ligne.gare_arrivee.id_gare,
                        ligne.date_creation,
                    ),
                )

                resultat = cursor.fetchone()

                if resultat is None:
                    raise Exception("Aucun identifiant retourné après l'insertion.")  # ruff: ignore[raise-vanilla-class]

                ligne.id_ligne = resultat["id_ligne"]

            connection.commit()
            return True

        except Exception:
            connection.rollback()
            raise

    def modifier_ligne(
        self,
        id_ligne: int,
        gare_depart: Gare,
        gare_arrivee: Gare,
    ) -> Ligne | None:
        """Modifie une ligne existante et retourne la ligne modifiée."""

        requete = """
            UPDATE Ligne
            SET id_gare_depart = %s,
                id_gare_arrivee = %s
            WHERE id_ligne = %s;
        """

        connexion = DBConnection().connection

        try:
            with connexion.cursor() as cursor:
                cursor.execute(
                    requete,
                    (
                        gare_depart.id_gare,
                        gare_arrivee.id_gare,
                        id_ligne,
                    ),
                )

                modification_effectuee = cursor.rowcount > 0

            connexion.commit()

            if not modification_effectuee:
                return None

            return self.recherche_ligne(id_ligne)

        except Exception:
            connexion.rollback()
            raise

    def supprimer_ligne(self, id_ligne: int) -> bool:
        """Supprime une ligne si aucun trajet ne l'utilise."""

        requete = """
            DELETE FROM Ligne
            WHERE id_ligne = %s;
        """

        connexion = DBConnection().connection

        try:
            with connexion.cursor() as cursor:
                cursor.execute(requete, (id_ligne,))
                suppression_effectuee = cursor.rowcount > 0

            connexion.commit()
            return suppression_effectuee

        except psycopg2.errors.ForeignKeyViolation:
            connexion.rollback()
            raise PermissionError(
                "Impossible de supprimer cette ligne : elle est utilisée par un ou plusieurs trajets."
            )

        except Exception:
            connexion.rollback()
            raise

    def recherche_ligne(self, id_ligne: int) -> Ligne | None:
        """Recherche une ligne à partir de son identifiant."""

        requete = """
            SELECT
                id_ligne,
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

        gare_depart = gare_dao.recherche_gare(resultat["id_gare_depart"])

        gare_arrivee = gare_dao.recherche_gare(resultat["id_gare_arrivee"])

        return Ligne(
            resultat["id_ligne"], gare_depart, gare_arrivee, resultat["date_creation"]
        )

    def rechercher_ids_par_gares(self, nom_depart: str, nom_arrivee: str) -> list[int]:
        requete = """
        SELECT l.id_ligne
        FROM Ligne AS l
        JOIN Gare AS depart ON depart.id_gare = l.id_gare_depart
        JOIN Gare AS arrivee ON arrivee.id_gare = l.id_gare_arrivee
        WHERE LOWER(depart.nom) = LOWER(%s)
          AND LOWER(arrivee.nom) = LOWER(%s)
        LIMIT 2
    """
        with DBConnection().connection.cursor() as cursor:
            cursor.execute(
                requete,
                (nom_depart.strip(), nom_arrivee.strip()),
            )
            return [ligne["id_ligne"] for ligne in cursor.fetchall()]
