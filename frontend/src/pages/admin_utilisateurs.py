import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin
from utils.helpers import afficher_resultat
from utils.page_setup import setup_page

logger = setup_page("admin_utilisateurs", "Administration", min_level="ADMIN")

st.title("Gestion des rôles")

# À adapter aux valeurs acceptées par ModificationRoleModel.nouvelle_habilitation
NIVEAUX = ["CLIENT", "COLLAB", "ADMIN"]

with st.form("role"):
    id_utilisateur = st.number_input("ID de l'utilisateur", min_value=1, step=1)
    niveau = st.selectbox("Nouveau niveau", NIVEAUX)
    envoyer = st.form_submit_button("Modifier le rôle")

if envoyer:
    res = api_client.put(
        chemin("utilisateurs", "/role"),
        json={
            "id_utilisateur": int(id_utilisateur),
            "nouvelle_habilitation": niveau,
        },
    )
    if afficher_resultat(res, "Habilitation modifiée."):
        logger.info(f"Rôle de l'utilisateur {id_utilisateur} -> {niveau}")
