import os
from collections.abc import Iterator, Optional  # au lieu de from typing import Iterator
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

BASE_URL = "https://api.sncf.com/v1/coverage/sncf/"
TIMEOUT = 10  # secondes

# On veut uniquement des trajets en train : on exclut les autres modes.
MODES_EXCLUS = [
    "physical_mode:Bus",
    "physical_mode:BusRapidTransit",
    "physical_mode:Coach",
    "physical_mode:Tramway",
    "physical_mode:Metro",
]

# Codes d'erreur Navitia signifiant "trajet non vérifiable / impossible"
ERREURS_TRAJET_IMPOSSIBLE = {
    "date_out_of_bounds",
    "no_origin",
    "no_destination",
    "unknown_object",
    "no_solution",
}


class ApiSncfError(Exception):
    """API SNCF injoignable ou réponse invalide.

    Dans ce cas, la faisabilité d'un trajet ne peut pas être vérifiée
    (donc le trajet ne doit pas être planifié).
    """

    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class ApiSncfService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SNCF_API_KEY")
        if not self.api_key:
            raise RuntimeError("SNCF_API_KEY is missing. Add it to your .env file.")
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.auth = (self.api_key, "")
        self._cache_gares: dict[str, dict] = {}

    # ------------------------------------------------------------------ #
    # Outils internes
    # ------------------------------------------------------------------ #
    def _get(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        """
        GET JSON. Retourne None si l'API répond 404 (introuvable / pas de solution).
        Lève ApiSncfError si l'API est injoignable ou si la réponse est invalide.

        """
        url = f"{self.base_url}{endpoint}"
        try:
            reponse = self.session.get(url, params=params, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise ApiSncfError(f"API SNCF injoignable : {e}") from e

        if reponse.status_code == 404:
            return None

        if not reponse.ok:
            code = None
            try:
                code = reponse.json().get("error", {}).get("id")
            except ValueError:
                pass
            raise ApiSncfError(
                f"Erreur API SNCF (HTTP {reponse.status_code}, {code or 'inconnue'})",
                code=code,
            )

        try:
            return reponse.json()
        except ValueError as e:
            raise ApiSncfError("Réponse invalide de l'API SNCF") from e

    @staticmethod
    def _formater_gare(stop_area: dict) -> dict:
        coord = stop_area.get("coord") or {}
        return {
            "id": stop_area["id"],  # ex : "stop_area:SNCF:87471003"
            "nom": stop_area.get("name", ""),
            "latitude": float(coord["lat"]) if coord.get("lat") else None,
            "longitude": float(coord["lon"]) if coord.get("lon") else None,
        }

    # ------------------------------------------------------------------ #
    # Gares
    # ------------------------------------------------------------------ #
    def obtenir_tous_les_arrets(
        self, max_pages: int = 5, par_page: int = 100
    ) -> Iterator[dict]:
        """À titre d'exemple : parcourt les gares page par page.

        On ne peut pas récupérer toutes les gares d'un coup, `max_pages`
        limite donc le parcours.
        """
        for page in range(max_pages):
            data = self._get("stop_areas", {"count": par_page, "start_page": page})
            if not data or not data.get("stop_areas"):
                return
            for stop_area in data["stop_areas"]:
                gare = self._formater_gare(stop_area)
                self._cache_gares[gare["id"]] = gare
                yield gare
            total = data.get("pagination", {}).get("total_result", 0)
            if (page + 1) * par_page >= total:
                return

    def obtenir_arrets_par_nom(self, name: str, limite: int = 20) -> list[dict]:
        """Autocomplétion : retourne les gares dont le nom correspond à la saisie.

        Exemple : obtenir_arrets_par_nom("Rennes")
        -> [{"id": "stop_area:SNCF:87471003", "nom": "Rennes", "latitude": ..., "longitude": ...}]
        """
        name = (name or "").strip()
        if len(name) < 2:  # évite un appel API à chaque première lettre
            return []

        data = self._get("places", {"q": name, "type[]": "stop_area", "count": limite})

        gares = []
        for place in (data or {}).get("places", []):
            if place.get("embedded_type") != "stop_area":
                continue
            infos = place.get("stop_area", {})
            gare = self._formater_gare({
                "id": place["id"],
                "name": place.get("name"),
                "coord": infos.get("coord"),
            })
            self._cache_gares[gare["id"]] = gare
            gares.append(gare)
        return gares

    def obtenir_gare_par_id(self, gare_id: str) -> Optional[dict]:
        """Retourne la gare correspondant à l'id SNCF, ou None si elle n'existe pas."""
        if not gare_id:
            return None
        if gare_id in self._cache_gares:
            return self._cache_gares[gare_id]

        data = self._get(f"stop_areas/{gare_id}")
        stop_areas = (data or {}).get("stop_areas") or []
        if not stop_areas:
            return None

        gare = self._formater_gare(stop_areas[0])
        self._cache_gares[gare["id"]] = gare
        return gare

    def gare_existe(self, gare_id: str) -> bool:
        return self.obtenir_gare_par_id(gare_id) is not None

    # ------------------------------------------------------------------ #
    # Faisabilité et durée d'un trajet
    # ------------------------------------------------------------------ #
    def calculer_duree_trajet(
        self, gare_depart_id: str, gare_arrivee_id: str, date_depart: datetime
    ) -> Optional[timedelta]:
        """Vérifie qu'un trajet en train est possible et retourne sa durée.

        - Retourne un timedelta si un trajet en train existe.
        - Retourne None si aucun trajet en train n'est possible.
        - Lève ApiSncfError si l'API est indisponible (faisabilité invérifiable :
          le trajet ne doit alors pas être planifié).
        """
        params = {
            "from": gare_depart_id,
            "to": gare_arrivee_id,
            "datetime": date_depart.strftime("%Y%m%dT%H%M%S"),
            "datetime_represents": "departure",
            "count": 3,
            "forbidden_uris[]": MODES_EXCLUS,
        }

        try:
            data = self._get("journeys", params)
        except ApiSncfError as e:
            if e.code in ERREURS_TRAJET_IMPOSSIBLE:
                return None
            raise

        # On garde les itinéraires qui contiennent au moins un tronçon de transport public
        itineraires = [
            j
            for j in (data or {}).get("journeys", [])
            if any(s.get("type") == "public_transport" for s in j.get("sections", []))
        ]
        if not itineraires:
            return None

        return timedelta(seconds=min(j["duration"] for j in itineraires))

    def trajet_possible(
        self, gare_depart_id: str, gare_arrivee_id: str, date_depart: datetime
    ) -> bool:
        return (
            self.calculer_duree_trajet(gare_depart_id, gare_arrivee_id, date_depart)
            is not None
        )


# Test rapide
if __name__ == "__main__":
    api = ApiSncfService()
    rennes = api.obtenir_arrets_par_nom("Rennes")[0]
    paris = api.obtenir_arrets_par_nom("Paris Montparnasse")[0]
    print(rennes, paris)

    demain_8h = (datetime.now() + timedelta(days=1)).replace(
        hour=8, minute=0, second=0, microsecond=0
    )
    print("Durée :", api.calculer_duree_trajet(rennes["id"], paris["id"], demain_8h))


# Pour obtenir une gare avec un nom précis, on peut utiliser l'endpoint "places" avec le paramètre de requête "q" pour spécifier le nom de la gare. Par exemple, pour obtenir des informations sur la gare d'Abancourt, on peut faire une requête GET à l'URL suivante :
# https://api.sncf.com/v1/coverage/sncf/places?q=Abancourt&type[]=stop_area
