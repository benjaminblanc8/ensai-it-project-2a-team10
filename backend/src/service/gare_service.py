from business_object.gare import Gare
from dao.gare_dao import GareDao
from fastapi import HTTPException
from service.api_sncf_service import ApiSncfError, ApiSncfService
from utils.log_utils import log


class GareService:
    """Service qui gère les gares (ajout, recherche, suppression)."""

    def __init__(self):
        self.api_sncf_service = ApiSncfService()
        self.dao = GareDao()

    @log
    def ajout_gare(self, gare: Gare) -> Gare:
        """Trouve l'identifiant SNCF de la gare et l'enregistre en base."""
        nom_normalise = gare.nom.strip().casefold()

        try:
            resultats = self.api_sncf_service.obtenir_arrets_par_nom(gare.nom)
        except ApiSncfError as exc:
            raise HTTPException(
                status_code=502,
                detail="La recherche de gare auprès de la SNCF a échoué.",
            ) from exc

        ids_sncf = {
            resultat["id_gare_sncf"]
            for resultat in resultats
            if (resultat.get("nom") or "").strip().casefold() == nom_normalise
            and resultat.get("id_gare_sncf")
        }

        if not ids_sncf:
            raise HTTPException(
                status_code=404,
                detail="Aucune gare SNCF ne correspond à ce nom.",
            )

        if len(ids_sncf) > 1:
            raise HTTPException(
                status_code=409,
                detail="Plusieurs gares SNCF portent ce nom.",
            )

        gare.id_gare_sncf = ids_sncf.pop()

        if not self.dao.creer_gare(gare):
            raise HTTPException(
                status_code=400,
                detail="Échec de la création de la gare.",
            )

        return gare
    
    @log
    def recherche_gare(self, id: int):
        """Recherche une gare à partir de son id.

        Args:
            id (int): l'id de la gare recherchée.

        Returns:
            Gare: La gare correspondant au nom donné.

        Raises:
            HTTPException: 404 si aucune gare ne correspond à cet id.
        """
        gare = self.dao.recherche_gare(id)

        if not gare:
            raise HTTPException(status_code=404, detail="Gare introuvable")

        return gare

    @log
    def recherche_gare_par_nom(self, nom_gare: int):
        """ recherche les gares par leurs noms"""
        list_gare = self.dao.recherche_gare_par_nom(nom_gare)

        if len(list_gare) == 0:
            raise HTTPException(status_code=404, detail="Gares introuvables")
   
        return list_gare

    @log
    def supprimer_gare(self, id_gare: int):
        """Supprime une gare à partir de son identifiant.

        Args:
            id_gare (int): L'identifiant de la gare à supprimer.

        Returns:
            Gare: La gare qui vient d'être supprimée.

        Raises:
            HTTPException: 404 si la gare n'existe pas.
        """
        gare = self.dao.recherche_gare(id_gare)

        if not gare:
            raise HTTPException(status_code=404, detail="Gare introuvable")

        self.dao.supprimer_gare(id_gare)

        return gare
