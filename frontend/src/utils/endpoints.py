"""Résolution des URL du backend.

Le préfixe de chaque routeur (include_router(prefix=...)) n'est connu que dans
le main.py du backend. On le trouve, dans l'ordre :
  1. variable d'environnement  PREFIX_<RESSOURCE>  (ex. PREFIX_UTILISATEURS=/utilisateur)
  2. détection automatique via /openapi.json du backend (grâce aux tags des routes)
  3. valeur par défaut ci-dessous
"""

import os

from utils.api_client import api_client

# ressource -> (tag FastAPI, préfixe par défaut)
# Défauts = cahier des charges (routes au singulier)
RESSOURCES = {
    "inscription": ("Inscription", "/inscription"),
    "connexion": ("Connexion", "/connexion"),
    "utilisateurs": ("Utilisateurs", "/utilisateur"),
    "gares": ("Gares", "/gare"),
    "api_sncf": ("API SNCF", "/api_sncf"),
    "lignes": ("Lignes", "/ligne"),
    "trajets": ("Trajets", "/trajet"),
    "reservations": ("Réservations", "/reservation"),
}

_detectes: dict[str, str] = {}
_openapi: dict = {}


def _prefixe_commun(chemins: list[str]) -> str:
    """Préfixe commun à des chemins, coupé avant le premier paramètre {x}."""
    listes = []
    for chemin in chemins:
        segments = []
        for segment in chemin.strip("/").split("/"):
            if segment.startswith("{"):
                break
            segments.append(segment)
        listes.append(segments)
    commun = os.path.commonprefix(listes)
    return "/" + "/".join(commun) if commun else ""


def _detecter() -> None:
    """Remplit _detectes à partir de /openapi.json (une fois, si le backend répond)."""
    if _detectes:
        return
    res = api_client.get("/openapi.json")
    if res["status_code"] != 200 or not isinstance(res["data"], dict):
        return
    _openapi.update(res["data"])

    par_tag: dict[str, list[str]] = {}
    for chemin, operations in res["data"].get("paths", {}).items():
        for operation in operations.values():
            for tag in operation.get("tags", []):
                par_tag.setdefault(tag, []).append(chemin)

    for ressource, (tag, _) in RESSOURCES.items():
        if par_tag.get(tag):
            prefixe = _prefixe_commun(par_tag[tag])
            if prefixe:
                _detectes[ressource] = prefixe


def prefixe(ressource: str) -> str:
    env = os.getenv(f"PREFIX_{ressource.upper()}")
    if env:
        return env.rstrip("/")
    _detecter()
    return _detectes.get(ressource, RESSOURCES[ressource][1])


def chemin(ressource: str, suffixe: str = "/") -> str:
    """Ex. chemin("gares", "/id/3") -> "/gares/id/3" (selon le préfixe réel)."""
    return f"{prefixe(ressource)}{suffixe}"


def etat_routes() -> dict[str, str]:
    """Préfixes utilisés actuellement (pour l'affichage de diagnostic)."""
    return {ressource: prefixe(ressource) for ressource in RESSOURCES}


def liste_routes() -> list[str]:
    """Routes réellement exposées par le backend (pour le diagnostic)."""
    _detecter()
    routes = []
    for chemin_api, operations in _openapi.get("paths", {}).items():
        for methode in operations:
            routes.append(f"{methode.upper()} {chemin_api}")
    return sorted(routes, key=lambda r: r.split(" ", 1)[1])
