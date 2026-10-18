
from business_object.niveau_habilitation import NiveauHabilitation
from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao


class UtilisateurService:

    def __init__(self):
        """Initialise le DAO utilisé par le service."""
        self.utilisateur_dao = UtilisateurDao()

    def creer_compte(self, pseudo: str, mdp: str) -> Utilisateur:
        """Crée un compte avec le rôle CLIENT."""

        if not pseudo or not pseudo.strip():
            raise ValueError("Le pseudo ne peut pas être vide.")

        if not mdp or len(mdp) < 8:
            raise ValueError(
                "Le mot de passe doit contenir au moins 8 caractères."
            )

        pseudo = pseudo.strip()

        # Vérifier que le pseudo n'existe pas déjà
        utilisateur_existant = (
            self.utilisateur_dao.recherche_par_pseudo(pseudo)
        )

        if utilisateur_existant is not None:
            raise ValueError("Ce pseudo est déjà utilisé.")

        # Tout nouvel utilisateur est CLIENT
        utilisateur = Utilisateur(
            None,
            pseudo,
            mdp,
            NiveauHabilitation.CLIENT
        )

        # Le DAO hashe le mot de passe avant l'INSERT
        self.utilisateur_dao.create(utilisateur)

        # On recharge l'utilisateur depuis la base
        # pour récupérer son mot de passe hashé
        return self.utilisateur_dao.recherche_utilisateur(
            utilisateur.id_utilisateur
        )

    def connexion(self, pseudo: str, mdp: str) -> Utilisateur | None:
        """Vérifie les identifiants de connexion."""

        utilisateur = self.utilisateur_dao.recherche_par_pseudo(
            pseudo
        )

        if utilisateur is None:
            return None

        if not utilisateur.verifier_mdp(mdp):
            return None

        return utilisateur

    def rechercher_utilisateur(
        self, id_utilisateur: int
    ) -> Utilisateur | None:
        """Recherche un utilisateur par son identifiant."""

        return self.utilisateur_dao.recherche_utilisateur(
            id_utilisateur
        )

    def modifier_habilitation(
        self,
        administrateur: Utilisateur,
        id_utilisateur: int,
        nouveau_niveau: NiveauHabilitation
    ) -> bool:
        """Modifie le rôle d'un utilisateur si le demandeur est ADMIN."""

        # Vérifier les droits en base, pas seulement
        # ceux déclarés dans l'objet Python fourni
        admin_bdd = self.utilisateur_dao.recherche_utilisateur(
            administrateur.id_utilisateur
        )

        if (
            admin_bdd is None
            or admin_bdd.niveau != NiveauHabilitation.ADMIN
        ):
            raise PermissionError(
                "Seul un administrateur peut modifier les habilitations."
            )

        # Modifier le rôle
        return self.utilisateur_dao.update(
            id_utilisateur,
            nouveau_niveau
        )
