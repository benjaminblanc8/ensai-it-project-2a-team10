from datetime import datetime

from pydantic import BaseModel, Field


class TrajetModel(BaseModel):
    """Modèle de données pour la création d'un trajet."""

    id_ligne: int
    date_heure_depart: datetime
    nb_places: int
    tarif: float


class TrajetReadModel(BaseModel):
    """Modèle de données pour la lecture d'un trajet."""

    id_trajet: int
    id_ligne: int
    date_heure_depart: datetime
    duree_minutes: int
    nb_places: int
    tarif: float
    places_reservees: int
    places_disponibles: int


class TrajetCreationModel(BaseModel):
    """Modèle de données pour la création d'un trajet."""

    nom_gare_depart: str
    nom_gare_arrivee: str
    date_heure_depart: datetime
    nb_places: int = Field(gt=0)
    tarif: float = Field(ge=0)
