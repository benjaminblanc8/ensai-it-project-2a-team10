from pydantic import BaseModel


class GareModel(BaseModel):
    nom: str
    ville: str


class GareReadModel(BaseModel):
    id: str
    nom: str
    ville: str