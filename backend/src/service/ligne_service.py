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

    def creer(self, gare_depart: Gare, gare_arrivee: Gare) -> Ligne:
        """Crée une ligne entre deux gares existantes.

        Parameters
        ----------
        gare_depart : Gare
            La gare de départ.
        gare_arrivee : Gare
            La gare d'arrivée.

        Returns
        -------
        Ligne
            La ligne créée entre les deux gares.

        Raises:
            HTTPException: 400 si les gares sont identiques.
            HTTPException: 404 si les gares ne sont pas trouvées.
            HTTPException: 409 si une ligne existe déjà entre ces deux gares.
        """

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

    def modifier_ligne(
        self, id_ligne: int, gare_depart: Gare, gare_arrivee: Gare
    ) -> Ligne:
        """Modifie une ligne existante avec de nouvelles gares de départ et d'arrivée.

        Parameters
        ----------
        id_ligne : int
            L'identifiant de la ligne à modifier.
        gare_depart : Gare
            La nouvelle gare de départ.
        gare_arrivee : Gare
            La nouvelle gare d'arrivée.

        Returns
        -------
        Ligne
            La ligne modifiée.

        Raises
        --------
        HTTPException: 400 si les gares sont identiques.
        HTTPException: 404 si la ligne n'existe pas.
        HTTPException: 409 si une ligne existe déjà entre les nouvelles gares.
        """

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

    def rechercher_ligne(self, id_ligne: int) -> Ligne:
        """Recherche une ligne à partir de son identifiant."""
        return self.dao.recherche_ligne(id_ligne)

    def supprimer_ligne(self, id_ligne: int) -> None:
        """Supprime une ligne à partir de son identifiant."""
        return self.dao.supprimer_ligne(id_ligne)

    def rechercher_ligne_par_gares(
        self, nom_depart: str, nom_arrivee: str
    ) -> Ligne | None:
        """Recherche une ligne à partir des noms des gares de départ et d'arrivée.

        Parameters
        ----------
        nom_depart : str
            Le nom de la gare de départ.
        nom_arrivee : str
            Le nom de la gare d'arrivée.

        Returns
        -------
        Ligne | None
            La ligne trouvée ou None si aucune ligne ne correspond.

        Raises
        ------
        HTTPException: 409 si plusieurs lignes correspondent aux noms des gares.
        """

        ids_lignes = self.dao.rechercher_ids_par_gares(nom_depart, nom_arrivee)

        if not ids_lignes:
            return None

        if len(ids_lignes) > 1:
            raise HTTPException(
                status_code=409,
                detail="Plusieurs lignes correspondent à ces noms de gares.",
            )

        return self.rechercher_ligne(ids_lignes[0])
