from pydantic import BaseModel


class GareModel(BaseModel):
    """Modèle pour représenter une gare."""

    nom: str
    ville: str


class GareReadModel(BaseModel):
    """Modèle pour représenter une gare lue depuis la base de données."""

    id_gare: int | None = None
    nom: str
    ville: str | None = None
    id_gare_sncf: str | None = None
