from pydantic import BaseModel


class GareModel(BaseModel):
    nom: str
    ville: str
    id_gare_sncf: str


class GareReadModel(BaseModel):
    id_gare: int | None = None
    nom: str
    ville: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    id_gare_sncf: str