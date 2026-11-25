from datetime import date

from pydantic import BaseModel, Field
from schema.gare_model import GareReadModel


class LigneModel(BaseModel):
    """Modèle de données pour la création d'une ligne."""

    nom_gare_depart: str = Field(min_length=1)
    nom_gare_arrivee: str = Field(min_length=1)


class LigneReadModel(BaseModel):
    """Modèle de données pour la lecture d'une ligne."""

    id_ligne: int
    gare_depart: GareReadModel
    gare_arrivee: GareReadModel
    date_creation: date


class LigneCreateModel(BaseModel):
    """Modèle de données pour la création d'une ligne."""

    id_gare_depart: int
    id_gare_arrivee: int


class LigneReadUpdateModel(BaseModel):
    """Modèle de données pour la lecture et la mise à jour d'une ligne."""

    id_ligne: int
    gare_depart: GareReadModel
    gare_arrivee: GareReadModel


class LigneUpdateModel(BaseModel):
    """Modèle de données pour la mise à jour d'une ligne."""

    id_ligne: int
    id_gare_depart: int
    id_gare_arrivee: int
