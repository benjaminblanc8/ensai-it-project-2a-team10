from datetime import date

from pydantic import BaseModel, Field
from schema.gare_model import GareModel


class LigneModel(BaseModel):
    nom_gare_depart: str = Field(min_length=1)
    nom_gare_arrivee: str = Field(min_length=1)


class LigneReadModel(BaseModel):
    id_ligne: int
    gare_depart: GareModel
    gare_arrivee: GareModel
    date_creation: date


class LigneCreateModel(BaseModel):
    id_gare_depart: int
    id_gare_arrivee: int


class LigneReadUpdateModel(BaseModel):
    id_ligne: int
    gare_depart: GareModel
    gare_arrivee: GareModel


class LigneUpdateModel(BaseModel):
    id_ligne: int
    id_gare_depart: int
    id_gare_arrivee: int
