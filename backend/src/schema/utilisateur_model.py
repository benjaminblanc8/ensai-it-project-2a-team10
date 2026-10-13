from business_object.niveau_habilitation import NiveauHabilitation
from pydantic import BaseModel


class UtilisateurModel(BaseModel):
    pseudo: str
    mdp: str


class ModificationRoleModel(BaseModel):
    id_utilisateur: int
    nouvelle_habilitation: NiveauHabilitation