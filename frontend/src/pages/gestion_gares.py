import pandas as pd
import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin
from utils.helpers import afficher_erreur, afficher_resultat
from utils.page_setup import setup_page

logger = setup_page("gestion_gares", "Gestion des gares", min_level="COLLAB")

st.title("Gares")

tab_base, tab_ajout, tab_suppr = st.tabs(
    ["Chercher en base", "Ajouter une gare", "Supprimer"]
)

with tab_base:
    nom = st.text_input("Nom de la gare", key="base_nom")
    if st.button("Chercher", key="base_btn"):
        res = api_client.get(chemin("gares", f"/nom_gare/{nom}"))
        if res["status_code"] == 200:
            st.dataframe(pd.DataFrame(res["data"]), hide_index=True)
        else:
            afficher_erreur(res)

with tab_ajout:
    st.caption(
        "Le backend vérifie que le nom correspond exactement à une gare de l'API SNCF "
        "et récupère lui-même l'identifiant SNCF. Cherche d'abord la gare, puis ajoute-la."
    )
    nom_sncf = st.text_input("Nom de la gare (API SNCF)", key="sncf_nom")
    if st.button("Chercher sur l'API SNCF"):
        res = api_client.get(chemin("api_sncf", f"/{nom_sncf}"))
        if res["status_code"] == 200:
            st.session_state["gares_sncf"] = res["data"]
        else:
            st.session_state["gares_sncf"] = []
            afficher_erreur(res)

    gares_sncf = st.session_state.get("gares_sncf", [])
    if gares_sncf:
        st.dataframe(pd.DataFrame(gares_sncf), hide_index=True)
        idx = st.selectbox(
            "Gare à ajouter en base",
            range(len(gares_sncf)),
            format_func=lambda i: gares_sncf[i].get("nom", "?"),
        )
        gare = gares_sncf[idx]
        ville = st.text_input("Ville", value=gare.get("ville") or "", key="ajout_ville")
        if st.button("Ajouter cette gare", type="primary"):
            res = api_client.post(
                chemin("gares", "/"),
                json={
                    "nom": gare.get("nom"),
                    "ville": ville,
                    "id_gare_sncf": gare.get("id_gare_sncf"),
                },
            )
            if afficher_resultat(res, "Gare ajoutée."):
                logger.info(f"Gare ajoutée : {gare.get('nom')}")

with tab_suppr:
    id_gare = st.number_input("ID de la gare", min_value=1, step=1)
    if st.button("Supprimer la gare"):
        res = api_client.delete(chemin("gares", f"/{int(id_gare)}"))
        if afficher_resultat(res, "Gare supprimée."):
            logger.info(f"Gare supprimée : {id_gare}")
