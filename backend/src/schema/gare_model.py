from pydantic import BaseModel


class GareModel(BaseModel):
    nom: str
    ville: str
    latitude: float
    longitude: float


class GareReadModel(BaseModel):
    id: str
    nom: str
    ville: str | None = None
    latitude: float
    longitude: float
