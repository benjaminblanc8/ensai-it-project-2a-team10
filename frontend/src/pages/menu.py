import streamlit as st
from utils.auth_guard import LEVELS, niveau_effectif
from utils.page_setup import setup_page

logger = setup_page("menu", "Menu", min_level="CLIENT")

niveau = niveau_effectif()


def carte(icone: str, titre: str, description: str, page: str):
    """Une carte avec un titre, une courte description et un bouton d'accès."""
    with st.container(border=True):
        st.markdown(f"#### {icone} {titre}")
        st.caption(description)
        if st.button("Ouvrir", key=f"menu_{page}"):
            st.switch_page(page)


st.title(f"Bonjour {st.session_state.get('pseudo', '')} 👋")

st.subheader("Voyager")
c1, c2 = st.columns(2)
with c1:
    carte("🔎", "Rechercher un trajet", "Trouve un trajet entre deux gares et réserve ta place.",
          "pages/recherche_trajets.py")
with c2:
    carte("🎫", "Mes réservations", "Consulte ou annule tes réservations.",
          "pages/mes_reservations.py")

if niveau >= LEVELS["COLLAB"]:
    st.subheader("Gestion du réseau")
    c1, c2, c3 = st.columns(3)
    with c1:
        carte("🚉", "Gares", "Ajouter ou supprimer des gares.", "pages/gestion_gares.py")
    with c2:
        carte("🛤️", "Lignes", "Créer et modifier les lignes.", "pages/gestion_lignes.py")
    with c3:
        carte("🕒", "Trajets", "Planifier les trajets et leurs tarifs.", "pages/gestion_trajets.py")

if niveau >= LEVELS["ADMIN"]:
    st.subheader("Administration")
    carte("🛡️", "Utilisateurs", "Modifier le niveau d'habilitation d'un utilisateur.",
          "pages/admin_utilisateurs.py")