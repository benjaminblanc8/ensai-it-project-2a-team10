from datetime import date

from pydantic import BaseModel, Field
from schema.gare_model import GareReadModel


class LigneModel(BaseModel):
    id_gare_depart: int
    id_gare_arrivee: int


class LigneReadModel(BaseModel):
    id_ligne: int
    gare_depart: GareReadModel
    gare_arrivee: GareReadModel
    date_creation: date


class LigneCreateModel(BaseModel):
    id_gare_depart: int
    id_gare_arrivee: int


class LigneReadUpdateModel(BaseModel):
    id_ligne: int
    gare_depart: GareReadModel
    gare_arrivee: GareReadModel


class LigneUpdateModel(BaseModel):
    id_ligne: int
    id_gare_depart: int
    id_gare_arrivee: int