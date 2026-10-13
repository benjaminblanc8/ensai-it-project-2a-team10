from datetime import date

from pydantic import BaseModel
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