
from argon2 import PasswordHasher

from business_object.utilisateur import Utilisateur
from business_object.niveau_habilitation import NiveauHabilitation
from dao.db_connection import DBConnection


class UtilisateurDao:

    def __init__(self):
        """Initialise la connexion à la base de données."""
        self.db = DBConnection()
        self.connection = self.db.connection
        self.password_hasher = PasswordHasher()

    def create(self, utilisateur: Utilisateur) -> bool:
        """Ajoute un utilisateur avec un mot de passe hashé."""

        requete = """
            INSERT INTO Utilisateur (pseudo, mdp, niveau)
            VALUES (%s, %s, %s)
            RETURNING id_utilisateur;
        """

        mdp_hash = self.password_hasher.hash(
            utilisateur.get_mdp()
        )

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (
                        utilisateur.get_pseudo(),
                        mdp_hash,
                        utilisateur.get_niveau().name
                    )
                )

                resultat = cursor.fetchone()
                nouvel_id = resultat["id_utilisateur"]

            self.connection.commit()
            utilisateur.id_utilisateur = nouvel_id

            return True

        except Exception:
            self.connection.rollback()
            raise

    def recherche_utilisateur(
        self, id_utilisateur: int
    ) -> Utilisateur | None:
        """Recherche un utilisateur par son identifiant."""

        requete = """
            SELECT id_utilisateur, pseudo, mdp, niveau
            FROM Utilisateur
            WHERE id_utilisateur = %s;
        """

        with self.connection.cursor() as cursor:
            cursor.execute(requete, (id_utilisateur,))
            resultat = cursor.fetchone()

        if resultat is None:
            return None

        return Utilisateur(
            resultat["id_utilisateur"],
            resultat["pseudo"],
            resultat["mdp"],
            NiveauHabilitation[resultat["niveau"]]
        )

    def recherche_par_pseudo(
        self, pseudo: str
    ) -> Utilisateur | None:
        """Recherche un utilisateur par son pseudo."""

        requete = """
            SELECT id_utilisateur, pseudo, mdp, niveau
            FROM Utilisateur
            WHERE pseudo = %s;
        """

        with self.connection.cursor() as cursor:
            cursor.execute(requete, (pseudo,))
            resultat = cursor.fetchone()

        if resultat is None:
            return None

        return Utilisateur(
            resultat["id_utilisateur"],
            resultat["pseudo"],
            resultat["mdp"],
            NiveauHabilitation[resultat["niveau"]]
        )

    def update(
        self,
        id_utilisateur: int,
        habilitation: NiveauHabilitation
    ) -> bool:

        requete = """
            UPDATE Utilisateur
            SET niveau = %s
            WHERE id_utilisateur = %s;
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (
                        habilitation.name,
                        id_utilisateur
                    )
                )

                modification_effectuee = cursor.rowcount > 0

            self.connection.commit()
            return modification_effectuee

        except Exception:
            self.connection.rollback()
            raise
