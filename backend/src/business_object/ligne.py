class Ligne:
    def __init__(self, id_ligne, libelle, gares, date_creation):
        self.id_ligne = id_ligne
        self.libelle = libelle
        self.gares = gares
        self.date_creation = date_creation
    
    def dessert(self, gare):
        return gare in self.gares
    
    def position_gare(self, gare):
        if gare in self.gares:
            return self.gares.index(gare)
        else:
            return -1
    
    def __str__(self):
        return f"Ligne {self.libelle} (ID: {self.id_ligne}) - Gares: {[gare.nom for gare in self.gares]} - Date de création: {self.date_creation}"
    
    def __repr__(self):
        return f"Ligne({self.id_ligne}, {self.libelle}, {self.gares}, {self.date_creation})"
        