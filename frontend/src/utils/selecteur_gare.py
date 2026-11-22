"""Liste déroulante de gares alimentée en direct par l'API SNCF (via le backend)."""

from urllib.parse import quote

import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin

try:
    from streamlit_searchbox import st_searchbox
except ImportError:  # pip install streamlit-searchbox
    st_searchbox = None

MIN_CARACTERES = 2


def _chercher_gares(terme: str) -> list[tuple[str, str]]:
    """Appelée à chaque frappe : retourne [(libellé affiché, nom de la gare)]."""
    terme = (terme or "").strip()
    if len(terme) < MIN_CARACTERES:
        return []

    cache = st.session_state.setdefault("cache_recherche_gares", {})
    cle = terme.casefold()
    if cle not in cache:
        res = api_client.get(chemin("api_sncf", f"/{quote(terme, safe='')}"))
        # 404 = aucune gare ; erreur réseau = on n'affiche rien
        cache[cle] = res["data"] if res["status_code"] == 200 else []

    options, deja_vues = [], set()
    for gare in cache[cle]:
        nom = gare.get("nom")
        if not nom or nom in deja_vues:
            continue
        deja_vues.add(nom)
        ville = gare.get("ville")
        libelle = f"{nom} ({ville})" if ville and ville.casefold() not in nom.casefold() else nom
        options.append((libelle, nom))
    return options


def selecteur_gare(label: str, key: str, placeholder: str = "Tape au moins 2 lettres...") -> str | None:
    """Retourne le nom de la gare choisie (uniquement une gare connue de l'API SNCF), sinon None."""
    if st_searchbox is None:
        st.warning("Installe `streamlit-searchbox` pour la recherche dynamique (saisie libre en attendant).")
        return st.text_input(label, key=key) or None

    return st_searchbox(
        _chercher_gares,
        label=label,
        placeholder=placeholder,
        key=key,
        debounce=400,  # évite un appel à l'API SNCF à chaque lettre
    )
