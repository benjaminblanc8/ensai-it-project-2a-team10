import streamlit as st
from utils.auth_guard import LEVELS
from utils.page_setup import setup_page

logger = setup_page("menu", "Menu", min_level="CLIENT")

niveau = LEVELS.get(st.session_state.get("niveau"), 0)

st.title(f"Bonjour {st.session_state.get('pseudo', '')} 👋")

st.subheader("Voyager")
c1, c2 = st.columns(2)
with c1:
    st.page_link("pages/recherche_trajets.py", label="Rechercher et réserver un trajet")
with c2:
    st.page_link("pages/mes_reservations.py", label="Voir mes réservations")

if niveau >= LEVELS["COLLAB"]:
    st.subheader("Gestion du réseau")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.page_link("pages/gestion_gares.py", label="Gérer les gares")
    with c2:
        st.page_link("pages/gestion_lignes.py", label="Gérer les lignes")
    with c3:
        st.page_link("pages/gestion_trajets.py", label="Gérer les trajets")

if niveau >= LEVELS["ADMIN"]:
    st.subheader("Administration")
    st.page_link("pages/admin_utilisateurs.py", label="Gérer les rôles des utilisateurs")
