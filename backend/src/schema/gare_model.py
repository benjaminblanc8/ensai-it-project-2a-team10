from pydantic import BaseModel


class GareModel(BaseModel):
    id_gare: int | None = None
    nom: str
    ville: str | None = None
    id_gare_sncf: str | None = None