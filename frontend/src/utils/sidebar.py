import streamlit as st
from utils.auth_guard import LEVELS

SESSION_KEYS = ("access_token", "pseudo", "niveau", "resultats_trajets")


def deconnecter():
    for key in SESSION_KEYS:
        st.session_state.pop(key, None)


def render_sidebar():
    """Menu latéral qui n'affiche que les pages autorisées pour le rôle."""
    niveau = LEVELS.get(st.session_state.get("niveau"), 0)
    with st.sidebar:
        st.header("🚆 Billets de train")

        if not st.session_state.get("access_token"):
            st.page_link("pages/home.py", label="Connexion")
            return

        st.write(f"Connecté : **{st.session_state.get('pseudo', '?')}**")
        st.caption(f"Niveau : {st.session_state.get('niveau', 'inconnu')}")

        st.page_link("pages/menu.py", label="Menu")
        st.page_link("pages/recherche_trajets.py", label="Rechercher un trajet")
        st.page_link("pages/mes_reservations.py", label="Mes réservations")

        if niveau >= LEVELS["COLLAB"]:
            st.divider()
            st.page_link("pages/gestion_gares.py", label="Gares")
            st.page_link("pages/gestion_lignes.py", label="Lignes")
            st.page_link("pages/gestion_trajets.py", label="Trajets")

        if niveau >= LEVELS["ADMIN"]:
            st.divider()
            st.page_link("pages/admin_utilisateurs.py", label="Utilisateurs")

        st.divider()
        if st.button("Se déconnecter"):
            deconnecter()
            st.switch_page("pages/home.py")
