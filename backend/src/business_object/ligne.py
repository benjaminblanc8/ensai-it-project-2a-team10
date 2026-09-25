from gare import Gare
class Ligne:
    def __init__(self, id_ligne, libelle, gare_depart: Gare, gare_arrivee: Gare, date_creation):
        self.id_ligne = id_ligne
        self.libelle = libelle
        self.gare_depart = gare_depart
        self.gare_arrivee = gare_arrivee
        self.date_creation = date_creation

    def dessert(self, gare):
        ...
    
    def __str__(self):
        return f"Ligne {self.libelle} (ID: {self.id_ligne}) - Gares: {self.gare_depart.nom} -> {self.gare_arrivee.nom} - Date de création: {self.date_creation}"
    
    def __repr__(self):
        return f"Ligne({self.id_ligne}, {self.libelle}, {self.gare_depart}, {self.gare_arrivee}, {self.date_creation})"
        