from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from business_object.niveau_habilitation import NiveauHabilitation


class Utilisateur:

    def __init__(
        self,
        id_utilisateur: int,
        pseudo: str,
        mdp: str,
        niveau: NiveauHabilitation
    ):
        self.id_utilisateur = id_utilisateur
        self.__pseudo = pseudo
        self.__mdp = mdp
        self.niveau = niveau

    def __repr__(self):
        return (
            f"Utilisateur(id_utilisateur={self.id_utilisateur}, "
            f"pseudo='{self.__pseudo}', niveau={self.niveau})"
        )

    def __str__(self):
        return (
            f"Utilisateur {self.__pseudo} "
            f"(ID: {self.id_utilisateur}) - Niveau: {self.niveau.name}"
        )

    def get_id_utilisateur(self) -> int:
        return self.id_utilisateur

    def get_pseudo(self) -> str:
        return self.__pseudo

    def get_mdp(self) -> str:
        return self.__mdp

    def get_niveau(self) -> NiveauHabilitation:
        return self.niveau

    def verifier_mdp(self, mdp: str) -> bool:
        """Vérifie le mot de passe saisi contre le hash stocké."""
        try:
            return PasswordHasher().verify(self.__mdp, mdp)
        except (VerifyMismatchError, VerificationError):
            return False

    def verifier_role(self, role: NiveauHabilitation) -> bool:
        return self.niveau == role