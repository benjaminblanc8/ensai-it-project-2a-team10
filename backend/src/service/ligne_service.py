import datetime

from business_object.gare import Gare
from business_object.ligne import Ligne
from dao.ligne_dao import LigneDao


class LigneService:
    def creer(self, gare_depart: Gare, gare_arrivee: Gare):
        """Création d'une nouvelle ligne
        Args:
            gare_depart: Gare
            gare_arrivee: Gare
        Returns:
            l'objet Ligne est créée ou "None" si la création a échoué
        """
        nouvelle_ligne = Ligne(
            id_ligne=None,
            gare_depart=gare_depart,
            gare_arrivee=gare_arrivee,
            libelle=libelle,
            date_creation=datetime.date.today(),
        )

        return nouvelle_ligne if LigneDao().creer(nouvelle_ligne) else None

    def modifier_ligne(self, ligne: Ligne, gare_depart: Gare, gare_arrivee: Gare):
        return LigneDao().modifier(ligne)

    def rechercher_ligne(self, id_ligne: int):
        return LigneDao().rechercher(id_ligne)

    def supprimer_ligne(self, id_ligne: int):
        return LigneDao().delete(id_ligne)
