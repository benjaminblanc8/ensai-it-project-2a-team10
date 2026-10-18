from datetime import datetime

from pydantic import BaseModel


class TrajetModel(BaseModel):
    id_ligne: int
    date_heure_depart: datetime
    duree_minutes: int
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