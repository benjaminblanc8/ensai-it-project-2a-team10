from pydantic import BaseModel


class GareModel(BaseModel):
    nom: str
    ville: str
    latitude: float
    longitude: float


class GareReadModel(BaseModel):
    id_gare: int
    nom: str
    ville: str
    latitude: float
    longitude: float