from argon2 import PasswordHasher
from business_object.niveau_habilitation import NiveauHabilitation
from business_object.utilisateur import Utilisateur
from dao.db_connection import DBConnection


class UtilisateurDao:
    def __init__(self):
        """Initialise la connexion à la base de données."""
        self.db = DBConnection()
        self.connection = self.db.connection
        self.password_hasher = PasswordHasher()

    def creer(self, utilisateur: Utilisateur) -> bool:
        """Ajoute un utilisateur avec un mot de passe hashé.

        Parameters
        ----------
        utilisateur : Utilisateur
            L'utilisateur à ajouter.

        Returns
        -------
        bool
            True si l'ajout a été effectué, False sinon.

        Raises
        ------
        Exception
            Si une erreur survient lors de l'exécution de la requête SQL.
        """

        requete = """
            INSERT INTO Utilisateur (pseudo, mdp, niveau)
            VALUES (%s, %s, %s)
            RETURNING id_utilisateur;
        """

        mdp_hash = self.password_hasher.hash(utilisateur.get_mdp())

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    requete,
                    (utilisateur.get_pseudo, mdp_hash, utilisateur.get_niveau().name),
                )

                resultat = cursor.fetchone()
                nouvel_id = resultat["id_utilisateur"]

            self.connection.commit()
            utilisateur.id_utilisateur = nouvel_id

            return True

        except Exception:
            self.connection.rollback()
            raise

    def recherche_utilisateur(self, id_utilisateur: int) -> Utilisateur | None:
        """Recherche un utilisateur par son identifiant.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur à rechercher.

        Returns
        -------
        Utilisateur | None
            L'utilisateur trouvé ou None s'il n'existe pas.

        Raises
        ------
        Exception
            Si une erreur survient lors de l'exécution de la requête SQL.
        """

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
            NiveauHabilitation[resultat["niveau"]],
        )

    def recherche_par_pseudo(self, pseudo: str) -> Utilisateur | None:
        """Recherche un utilisateur par son pseudo.

        Parameters
        ----------
        pseudo : str
            Le pseudo de l'utilisateur à rechercher.

        Returns
        -------
        Utilisateur | None
            L'utilisateur trouvé ou None s'il n'existe pas.

        Raises
        ------
        Exception
            Si une erreur survient lors de l'exécution de la requête SQL.
        """

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
            NiveauHabilitation[resultat["niveau"]],
        )

    def update(self, id_utilisateur: int, habilitation: NiveauHabilitation) -> bool:
        """Met à jour l'habilitation d'un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            L'identifiant de l'utilisateur.
        habilitation : NiveauHabilitation
            Le nouveau niveau d'habilitation.

        Returns
        -------
        bool
            True si la mise à jour a été effectuée, False sinon.

        Raises
        ------
        Exception
            Si une erreur survient lors de l'exécution de la requête SQL.
        """

        requete = """
            UPDATE Utilisateur
            SET niveau = %s
            WHERE id_utilisateur = %s;
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(requete, (habilitation.name, id_utilisateur))

                modification_effectuee = cursor.rowcount > 0

            self.connection.commit()
            return modification_effectuee

        except Exception:
            self.connection.rollback()
            raise
