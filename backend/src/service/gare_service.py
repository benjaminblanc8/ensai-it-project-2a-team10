from dao.gare_dao import GareDao
from fastapi import HTTPException
from utils.log_utils import log


class GareService:
    """Service qui gère les gares (ajout, recherche, suppression)."""

    @log
    def ajout_gare(self, gare) -> object:
        """Ajoute une gare en base de données.

        Arg:
            gare (Gare): La gare à créer.

        Returns:
            Gare: La gare qui vient d'être créée.

        Raises:
            HTTPException: 400 si la création échoue.
        """
        if not GareDao().create_gare(gare):
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
        gare = GareDao().find_by_id(id)

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
        gare = GareDao().find_by_id(id_gare)

        if not gare:
            raise HTTPException(status_code=404, detail="Gare introuvable")

        GareDao().supprimer_gare(id_gare)

        return gare
