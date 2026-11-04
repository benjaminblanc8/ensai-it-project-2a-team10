from business_object.gare import Gare
from dao.gare_dao import GareDao
from fastapi import HTTPException
from service.api_sncf_service import ApiSncfService
from utils.log_utils import log


class GareService:
    """Service qui gère les gares (ajout, recherche, suppression)."""

    def __init__(self):
        self.api_sncf_service = ApiSncfService()
        self.dao = GareDao()

    @log
    def ajout_gare(self, gare: Gare) -> bool:
        """Ajoute une gare en base de données.

        Arg:
            gare (Gare): La gare à créer.

        Returns:
            Gare: La gare qui vient d'être créée.

        Raises:
            HTTPException: 400 si la création échoue.
        """
        # Vérification de l'existence des gares auprès de SNCF
        if not self.api_sncf_service.gare_existe_par_nom(gare.nom):
            raise HTTPException(status_code=404, detail="Cette gare n'existe pas.")
            return None

        creer_gare = self.dao.creer_gare(gare)

        if not creer_gare:
            raise HTTPException(
                status_code=400, detail="Échec de la création de la gare"
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
    def supprimer_gare(self, id_gare: int):
        """Supprime une gare à partir de son identifiant.

        Args:
            id_gare (int): L'identifiant de la gare à supprimer.

        Returns:
            Gare: La gare qui vient d'être supprimée.

        Raises:
            HTTPException: 404 si la gare n'existe pas.
        """
        gare = self.dao.find_by_id(id_gare)

        if not gare:
            raise HTTPException(status_code=404, detail="Gare introuvable")

        self.dao.supprimer_gare(id_gare)

        return gare
