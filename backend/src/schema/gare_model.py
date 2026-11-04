from pydantic import BaseModel


class GareModel(BaseModel):
    nom: str
    ville: str


class GareReadModel(BaseModel):
    id_gare: int | None = None
    nom: str
    ville: str | None = None
    id_gare_sncf: str | None = None