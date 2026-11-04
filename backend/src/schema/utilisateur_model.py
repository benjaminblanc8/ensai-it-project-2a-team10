from business_object.niveau_habilitation import NiveauHabilitation
from pydantic import BaseModel, Field


class UtilisateurModel(BaseModel):
    """Informations nécessaires à la création d'un compte."""

    pseudo: str = Field(min_length=3, max_length=50)
    mdp: str = Field(min_length=8, max_length=128)


class ModificationRoleModel(BaseModel):
    """Informations nécessaires à la modification d'une habilitation."""

    id_utilisateur: int
    nouvelle_habilitation: NiveauHabilitation


class UtilisateurResponseModel(BaseModel):
    """Informations publiques d'un utilisateur."""

    id: int
    pseudo: str
    habilitation: NiveauHabilitation


class ConnexionResponseModel(BaseModel):
    """Réponse retournée après une connexion réussie."""

    access_token: str
    token_type: str = "bearer"
    utilisateur: UtilisateurResponseModel