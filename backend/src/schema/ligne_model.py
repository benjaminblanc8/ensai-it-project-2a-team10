from datetime import date

from pydantic import BaseModel, Field
from schema.gare_model import GareReadModel


class LigneModel(BaseModel):
    libelle: str
    id_gare_depart: int
    id_gare_arrivee: int


class LigneReadModel(BaseModel):
    id_ligne: int
    libelle: str
    gare_depart: GareReadModel
    gare_arrivee: GareReadModel
    date_creation: date


class LigneCreateModel(BaseModel):
    libelle: str = Field(min_length=2, max_length=100)
    id_gare_depart: int
    id_gare_arrivee: int


class LigneUpdateModel(BaseModel):
    libelle: str = Field(min_length=2, max_length=100)
    id_gare_depart: int
    id_gare_arrivee: int
