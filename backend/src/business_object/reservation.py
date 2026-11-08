from business_object.trajet import Trajet
from business_object.utilisateur import Utilisateur


class Reservation:
    def __init__(self, id_reservation: int, utilisateur: Utilisateur, trajet: Trajet):
        self.utilisateur = utilisateur
        self.trajet = trajet
        self.id_reservation = id_reservation
 
    def get_places_restantes(self):
        return self.trajet.get_nb_places_disponibles()
