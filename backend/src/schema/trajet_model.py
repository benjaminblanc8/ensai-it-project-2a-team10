from datetime import datetime

from pydantic import BaseModel


class TrajetModel(BaseModel):
    id_ligne: int
    date_heure_depart: datetime
    nb_places: int
    tarif: float


class TrajetReadModel(BaseModel):
    id_trajet: int
    id_ligne: int
    date_heure_depart: datetime
    duree_minutes: int
    nb_places: int
    tarif: float
    places_reservees: int
    places_disponibles: int


class TrajetCreationModel(BaseModel):
    nom_gare_depart: str
    nom_gare_arrivee: str
    date_heure_depart: datetime
    nb_places: int
    tarif: float