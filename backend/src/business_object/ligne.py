from datetime import datetime

from business_object.gare import Gare


class Ligne:
    def __init__(
        self, id_ligne, gare_depart: Gare, gare_arrivee: Gare, date_creation: datetime
    ):
        self.id_ligne = id_ligne
        self.gare_depart = gare_depart
        self.gare_arrivee = gare_arrivee
        self.date_creation = date_creation

    def __str__(self):
        return f"Ligne (ID: {self.id_ligne}) - Gares: {self.gare_depart.nom} -> "
        "{self.gare_arrivee.nom} - Date de création: {self.date_creation}"

    def __repr__(self):
        return f"Ligne({self.id_ligne}, {self.gare_depart}, {self.gare_arrivee}, "
        "{self.date_creation})"
