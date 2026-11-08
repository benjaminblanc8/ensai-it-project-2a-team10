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

        if self.dao.rechercher_ids_par_gares(gare_depart.nom, gare_arrivee.nom):
            raise HTTPException(
                status_code=409,
                detail="Une ligne existe déjà entre ces deux gares.",
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

    def modifier_ligne(self, id_ligne: int, gare_depart: Gare, gare_arrivee: Gare):
        if gare_depart.id_gare == gare_arrivee.id_gare:
            raise HTTPException(
                status_code=400,
                detail="Les gares de départ et d'arrivée doivent être différentes.",
            )
        if not self.dao.recherche_ligne(id_ligne):
            raise HTTPException(
                status_code=404,
                detail=f"La ligne avec l'identifiant {id_ligne} n'existe pas.",
            )
        gare_depart = self.gare_service.recherche_gare(gare_depart.id_gare)
        gare_arrivee = self.gare_service.recherche_gare(gare_arrivee.id_gare)

        if not gare_depart or not gare_arrivee:
            raise HTTPException(
                status_code=404, detail="Une des gares sélectionnées n'existe pas."
            )

        ids_existants = self.dao.rechercher_ids_par_gares(
            gare_depart.nom, gare_arrivee.nom
        )
        if any(id != id_ligne for id in ids_existants):
            raise HTTPException(
                status_code=409,
                detail="Une ligne existe déjà entre ces deux gares.",
            )

        return self.dao.modifier_ligne(id_ligne, gare_depart, gare_arrivee)

    def rechercher_ligne(self, id_ligne: int):
        return self.dao.recherche_ligne(id_ligne)

    def supprimer_ligne(self, id_ligne: int):
        return self.dao.supprimer_ligne(id_ligne)

    def rechercher_ligne_par_gares(
        self, nom_depart: str, nom_arrivee: str
    ) -> Ligne | None:
        ids_lignes = self.dao.rechercher_ids_par_gares(nom_depart, nom_arrivee)

        if not ids_lignes:
            return None

        if len(ids_lignes) > 1:
            raise HTTPException(
                status_code=409,
                detail="Plusieurs lignes correspondent à ces noms de gares.",
            )

        return self.rechercher_ligne(ids_lignes[0])
