import datetime

from business_object.gare import Gare
from business_object.ligne import Ligne
from dao.ligne_dao import LigneDao
from fastapi import HTTPException
from service.api_sncf_service import ApiSncfService
from service.gare_service import GareService


class LigneService:
    def __init__(self):
        self.gare_service = GareService()
        self.api_sncf_service = ApiSncfService()
        self.dao = LigneDao()

    def creer(self, gare_depart: Gare, gare_arrivee: Gare):
        """Crée une ligne entre deux gares existantes."""

        if not gare_depart or not gare_arrivee:
            raise HTTPException(
                status_code=404,
                detail="La gare de départ ou d'arrivée est introuvable.",
            )

        # Vérification de l'existence des gares auprès de SNCF
        gare_depart = self.gare_service.recherche_gare(gare_depart.id_gare)
        gare_arrivee = self.gare_service.recherche_gare(gare_arrivee.id_gare)

        if not gare_depart or not gare_arrivee:
            raise HTTPException(
                status_code=404, detail="Une des gares sélectionnées n'existe pas."
            )

        if gare_depart.id_gare == gare_arrivee.id_gare:
            raise HTTPException(
                status_code=400,
                detail="Les gares de départ et d'arrivée doivent être différentes.",
            )

        nouvelle_ligne = Ligne(
            id_ligne=None,
            gare_depart=gare_depart,
            gare_arrivee=gare_arrivee,
            date_creation=datetime.date.today(),
        )

        if not self.dao.creer_ligne(nouvelle_ligne):
            raise HTTPException(
                status_code=500, detail="Échec de la création de la ligne."
            )

        return nouvelle_ligne

    def modifier_ligne(self, ligne: Ligne, gare_depart: Gare, gare_arrivee: Gare):
        return self.dao.modifier(ligne)

    def rechercher_ligne(self, id_ligne: int):
        return self.dao.recherche_ligne(id_ligne)

    def supprimer_ligne(self, id_ligne: int):
        return self.dao.delete(id_ligne)
