import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin
from utils.helpers import afficher_resultat
from utils.page_setup import setup_page

logger = setup_page("admin_utilisateurs", "Administration", min_level="ADMIN")

st.title("Gestion des habilitations")
st.caption(
    "Seul un ADMIN peut modifier le niveau d'un utilisateur, et uniquement celui "
    "d'un non-ADMIN (le serveur répond 403 sinon)."
)

NIVEAUX = ["CLIENT", "COLLAB", "ADMIN"]


def modifier_niveau(id_utilisateur: int, niveau: str) -> dict:
    """PUT /utilisateur/{id}/niveau (cahier des charges), sinon ancienne route /role."""
    res = api_client.put(
        chemin("utilisateurs", f"/{id_utilisateur}/niveau"),
        json={"niveau": niveau, "nouvelle_habilitation": niveau},
    )
    if res["status_code"] in (404, 405):
        res = api_client.put(
            chemin("utilisateurs", "/role"),
            json={"id_utilisateur": id_utilisateur, "nouvelle_habilitation": niveau},
        )
    return res


with st.form("niveau"):
    id_utilisateur = st.number_input("ID de l'utilisateur", min_value=1, step=1)
    niveau = st.selectbox("Nouveau niveau", NIVEAUX)
    envoyer = st.form_submit_button("Modifier le niveau")

if envoyer:
    res = modifier_niveau(int(id_utilisateur), niveau)
    if afficher_resultat(res, "Habilitation modifiée."):
        logger.info(f"Niveau de l'utilisateur {id_utilisateur} -> {niveau}")
