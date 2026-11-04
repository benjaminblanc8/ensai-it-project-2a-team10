from datetime import datetime

from business_object.gare import Gare


class Ligne:
    def __init__(
        self,
        id_ligne: int | None,
        gare_depart: Gare,
        gare_arrivee: Gare,
        date_creation: datetime,
    ):
        self.id_ligne = id_ligne
        self.gare_depart = gare_depart
        self.gare_arrivee = gare_arrivee
        self.date_creation = date_creation

    def __str__(self) -> str:
        return (
            f"Ligne (ID: {self.id_ligne}) - Gares: "
            f"{self.gare_depart.nom} → {self.gare_arrivee.nom} "
            f"- Date de création: {self.date_creation}"
        )

    def __repr__(self) -> str:
        return (
            f"Ligne(id_ligne={self.id_ligne!r}, "
            f"gare_depart={self.gare_depart!r}, "
            f"gare_arrivee={self.gare_arrivee!r}, "
            f"date_creation={self.date_creation!r})"
        )