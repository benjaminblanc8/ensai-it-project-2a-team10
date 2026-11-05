
from pydantic import BaseModel, ConfigDict

from datetime import datetime


class ReservationCreateModel(BaseModel):
    """Informations nécessaires pour réserver un trajet."""

    id_trajet: int


class ReservationUtilisateurReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_utilisateur: int
    pseudo: str
    niveau: str


class ReservationTrajetReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date_heure_depart: datetime
    duree_minutes: int
    nb_places: int
    tarif: float
    places_reservees: int


class ReservationReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_reservation: int
    utilisateur: ReservationUtilisateurReadModel
    trajet: ReservationTrajetReadModel


class ReservationResponseModel(BaseModel):
    """Réponse simplifiée après une création ou une annulation."""

    message: str
    id_reservation: int
