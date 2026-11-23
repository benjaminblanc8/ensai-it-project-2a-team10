"""Liste déroulante de gares avec autocomplétion, alimentée en direct par le backend.

Deux sources possibles :
  - "base" : gares déjà enregistrées en base      -> GET /gare/nom_gare/{nom}
  - "sncf" : gares connues de l'API SNCF          -> GET /api_sncf/{nom}
"""

from typing import Literal
from urllib.parse import quote

import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin

try:
    from streamlit_searchbox import st_searchbox
except ImportError:  # pip install streamlit-searchbox
    st_searchbox = None

MIN_CARACTERES = 2
Source = Literal["base", "sncf"]


def _url(source: Source, terme: str) -> str:
    terme_url = quote(terme, safe="")
    if source == "base":
        return chemin("gares", f"/nom_gare/{terme_url}")
    return chemin("api_sncf", f"/{terme_url}")


def _fabrique_recherche(source: Source):
    """Crée la fonction appelée à chaque frappe : retourne [(libellé, nom de la gare)]."""

    def chercher(terme: str) -> list[tuple[str, str]]:
        terme = (terme or "").strip()
        if len(terme) < MIN_CARACTERES:
            return []

        # La base est interrogée à chaque fois (une gare ajoutée doit apparaître
        # tout de suite) ; l'API SNCF, plus lente, est mise en cache.
        if source == "sncf":
            cache = st.session_state.setdefault("cache_recherche_gares_sncf", {})
            cle = terme.casefold()
            if cle not in cache:
                res = api_client.get(_url(source, terme))
                cache[cle] = res["data"] if res["status_code"] == 200 else []
            gares = cache[cle]
        else:
            res = api_client.get(_url(source, terme))
            gares = res["data"] if res["status_code"] == 200 else []  # 404 = aucune gare

        options, deja_vues = [], set()
        for gare in gares:
            nom = gare.get("nom")
            if not nom or nom in deja_vues:
                continue
            deja_vues.add(nom)
            ville = gare.get("ville")
            affiche_ville = ville and ville.casefold() not in nom.casefold()
            options.append((f"{nom} ({ville})" if affiche_ville else nom, nom))
        return options

    return chercher


def selecteur_gare(
    label: str,
    key: str,
    source: Source = "sncf",
    placeholder: str | None = None,
) -> str | None:
    """Retourne le nom de la gare choisie (uniquement une gare proposée par la source), sinon None."""
    if st_searchbox is None:
        st.warning("Installe `streamlit-searchbox` pour la recherche dynamique (saisie libre en attendant).")
        return st.text_input(label, key=key) or None

    if placeholder is None:
        placeholder = (
            "Gare enregistrée : tape au moins 2 lettres..."
            if source == "base"
            else "Gare SNCF : tape au moins 2 lettres..."
        )

    return st_searchbox(
        _fabrique_recherche(source),
        label=label,
        placeholder=placeholder,
        key=key,
        debounce=400,  # évite un appel au backend à chaque lettre
    )