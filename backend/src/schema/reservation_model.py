from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ReservationCreateModel(BaseModel):
    """Informations nécessaires pour réserver un trajet."""

    id_trajet: int


class ReservationUtilisateurReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_utilisateur: int
    pseudo: str = Field(
        validation_alias=AliasChoices("pseudo", "_Utilisateur__pseudo")
    )
    niveau: str


class ReservationTrajetReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_trajet: int
    date_heure_depart: datetime
    duree_minutes: int

    nb_places: int = Field(
        validation_alias=AliasChoices("nb_places", "_nb_places")
    )
    tarif: float = Field(
        validation_alias=AliasChoices("tarif", "_tarif")
    )
    places_reservees: int = Field(
        validation_alias=AliasChoices("places_reservees", "_places_reservees")
    )


class ReservationReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_reservation: int
    utilisateur: ReservationUtilisateurReadModel
    trajet: ReservationTrajetReadModel


class ReservationResponseModel(BaseModel):
    """Réponse simplifiée après une création ou une annulation."""

    message: str
    id_reservation: int
