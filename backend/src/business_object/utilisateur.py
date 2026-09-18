from backend.src.business_object.niveau_habilitation import NiveauHabilitation


class Utilisateur:
    def __init__(self, __id_utilisateur: int,
                 __pseudo: str,
                 __mdp: str,
                 __niveau: NiveauHabilitation):
        self.__id_utilisateur = __id_utilisateur
        self.__pseudo = __pseudo
        self.__mdp = __mdp
        self.__niveau = __niveau

    def __repr__(self):
        return f"Utilisateur(id_utilisateur={self.__id_utilisateur}, "
    "pseudo='{self.__pseudo}', email='{self.__email}', niveau={self.__niveau})" 
    
    def __str__(self):
        return f"Utilisateur {self.__pseudo} (ID: {self.__id_utilisateur}) -"
    "Email: {self.__email} - Niveau: {self.__niveau}"   
    
    def get_id_utilisateur(self) -> int:
        return self.__id_utilisateur
    
    def get_pseudo(self) -> str:
        return self.__pseudo
    
    def get_niveau(self) -> NiveauHabilitation:
        return self.__niveau
    
    def verifier_mdp(self, mdp: str) -> bool:
        # Méthode pour vérifier le mot de passe de l'utilisateur
        # Cette méthode devrait être implémentée pour vérifier le mot de passe
        # contre une valeur stockée (par exemple, un hachage de mot de passe).
        # Pour l'instant, elle retourne True pour simplifier.
        return True
    
    def verifier_role(self, role: NiveauHabilitation) -> bool:
        # Méthode pour vérifier si l'utilisateur a le rôle spécifié
        return self.__niveau == role
