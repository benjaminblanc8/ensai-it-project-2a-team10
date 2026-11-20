import logging
import time

import streamlit as st

# Même hiérarchie que NiveauHabilitation côté backend
LEVELS = {"CLIENT": 1, "COLLAB": 2, "ADMIN": 3}


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

    if min_level:
        current = LEVELS.get(st.session_state.get("niveau"), 0)
        if current < LEVELS[min_level]:
            st.error("Accès refusé : droits insuffisants pour cette page.")
            st.stop()
