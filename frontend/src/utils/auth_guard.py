import logging
import time

import streamlit as st

# Même hiérarchie que NiveauHabilitation côté backend (niveaux cumulatifs)
LEVELS = {"CLIENT": 1, "COLLAB": 2, "ADMIN": 3}


def niveau_effectif() -> int:
    """Niveau numérique de l'utilisateur.

    Si le rôle n'a pas pu être récupéré (niveau "INCONNU"), on n'étouffe rien :
    toutes les pages sont proposées et c'est le backend qui répond 403 si besoin.
    """
    niveau = st.session_state.get("niveau")
    if niveau == "INCONNU":
        return max(LEVELS.values())
    return LEVELS.get(niveau, 0)


def check_authentification(min_level: str | None = None):
    """Redirige vers l'accueil si non connecté, bloque la page si le rôle est insuffisant.

    Ce contrôle ne sert qu'à l'affichage : la vraie sécurité est
    `require_niveau` côté backend.
    """
    if not st.session_state.get("access_token"):
        logging.info("Not logged in, return to the home page")
        st.error("Connecte-toi pour accéder à cette page. Retour à l'accueil...")
        time.sleep(1)
        st.switch_page("pages/home.py")

    if min_level and niveau_effectif() < LEVELS[min_level]:
        st.error("Accès refusé : droits insuffisants pour cette page.")
        st.stop()
