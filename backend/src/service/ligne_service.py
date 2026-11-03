import datetime

from business_object.gare import Gare
from business_object.ligne import Ligne
from dao.ligne_dao import LigneDao


class LigneService:
    def __init__(self, gare_service):
        self.gare_service = gare_service
        self.dao = LigneDao()

    def creer(self, gare_depart: Gare, gare_arrivee: Gare):
        """Création d'une nouvelle ligne
        Args:
            gare_depart: Gare
            gare_arrivee: Gare
        Returns:
            l'objet Ligne est créée ou "None" si la création a échoué
        """

        if not gare_depart or not gare_arrivee:
            return None

        nouvelle_ligne = Ligne(
            id_ligne=None,
            gare_depart=gare_depart,
            gare_arrivee=gare_arrivee,
            date_creation=datetime.date.today(),
        )

        return nouvelle_ligne if self.dao.creer(nouvelle_ligne) else None

    def modifier_ligne(self, ligne: Ligne, gare_depart: Gare, gare_arrivee: Gare):
        return self.dao.modifier(ligne)

    def rechercher_ligne(self, id_ligne: int):
        return self.dao.rechercher(id_ligne)

    def supprimer_ligne(self, id_ligne: int):
        return self.dao.delete(id_ligne)

    def _verifier_gares(self, gare_depart_id, gare_arrivee_id):
        gare_depart = self.gare_service.recherche_gare(gare_depart_id)
        gare_arrivee = self.gare_service.recherche_gare(gare_arrivee_id)

        if not gare_depart or not gare_arrivee:
            return None, None

        if gare_depart.id_gare == gare_arrivee.id_gare:
            return None, None

        return gare_depart, gare_arrivee
