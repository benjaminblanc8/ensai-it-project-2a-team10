from src.business_object.gare import Gare
from src.business_object.ligne import Ligne
from datetime import datetime


class Trajet:
    def __init__(
        self,
        gare_depart: Gare,
        gare_arrivee: Gare,
        date_heure_depart: datetime,
        duree_minutes: int,
        ligne: Ligne,
        _nb_places: int,
        _tarif: float,
        _places_reservees: int = 0
    ):
        self.gare_depart = gare_depart
        self.gare_arrivee = gare_arrivee
        self.date_heure_depart = date_heure_depart
        self.duree_minutes = duree_minutes
        self.ligne = ligne
        self._nb_places = _nb_places
        self._tarif = _tarif
        self._places_reservees = _places_reservees

    def __repr__(self):
        return (f"Trajet(gare_depart={self.gare_depart}, gare_arrivee={self.gare_arrivee}, "
                f"date_heure_depart={self.date_heure_depart}, duree_minutes={self.duree_minutes}, "
                f"ligne={self.ligne}, nb_places={self._nb_places}, tarif={self._tarif}, "
                f"places_reservees={self._places_reservees})")
    
    def __str__(self):
        return (f"Trajet de {self.gare_depart.nom} à {self.gare_arrivee.nom} "
                f"le {self.date_heure_depart.strftime('%Y-%m-%d %H:%M')} "
                f"durée: {self.duree_minutes} minutes, ligne: {self.ligne.nom}, "
                f"places disponibles: {self._nb_places - self._places_reservees}, tarif: {self._tarif}€")
    
    def get_nb_places_disponibles(self) -> int:
        return self._nb_places - self._places_reservees
    
    def get_tarif(self) -> float:
        return self._tarif
    
    def get_places_reservees(self) -> int:
        return self._places_reservees
    
    def heure_arrivee(self) -> datetime:
        ...
        
    def places_restantes(self) -> int:
        return self._nb_places - self._places_reservees
    
    def est_complet(self) -> bool:
        return self._places_reservees >= self._nb_places
    
    