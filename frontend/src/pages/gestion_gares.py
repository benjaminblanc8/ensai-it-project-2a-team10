import pandas as pd
import streamlit as st
from utils.api_client import api_client
from utils.helpers import afficher_erreur, afficher_resultat
from utils.page_setup import setup_page

logger = setup_page("gestion_gares", "Gestion des gares", min_level="COLLAB")

st.title("Gares")

tab_base, tab_sncf, tab_manuel, tab_suppr = st.tabs(
    ["Chercher en base", "Importer depuis la SNCF", "Ajouter à la main", "Supprimer"]
)

with tab_base:
    nom = st.text_input("Nom de la gare", key="base_nom")
    if st.button("Chercher", key="base_btn"):
        res = api_client.get(f"/gares/nom_gare/{nom}")
        if res["status_code"] == 200:
            st.dataframe(pd.DataFrame(res["data"]), hide_index=True)
        else:
            afficher_erreur(res)

with tab_sncf:
    nom_sncf = st.text_input("Nom de la gare (API SNCF)", key="sncf_nom")
    if st.button("Interroger l'API SNCF"):
        res = api_client.get(f"/api-sncf/{nom_sncf}")
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
            format_func=lambda i: f"{gares_sncf[i].get('nom')} ({gares_sncf[i].get('ville', '')})",
        )
        if st.button("Ajouter cette gare"):
            g = gares_sncf[idx]
            res = api_client.post(
                "/gares/",
                json={
                    "nom": g.get("nom"),
                    "ville": g.get("ville"),
                    "id_gare_sncf": g.get("id_gare_sncf"),
                },
            )
            if afficher_resultat(res, "Gare ajoutée."):
                logger.info(f"Gare ajoutée : {g.get('nom')}")

with tab_manuel:
    with st.form("gare_manuelle"):
        nom_m = st.text_input("Nom")
        ville_m = st.text_input("Ville")
        id_sncf = st.text_input("Identifiant SNCF (ex. stop_area:SNCF:87391003)")
        ajouter = st.form_submit_button("Ajouter la gare")
    if ajouter:
        res = api_client.post(
            "/gares/",
            json={"nom": nom_m, "ville": ville_m, "id_gare_sncf": id_sncf or None},
        )
        afficher_resultat(res, "Gare ajoutée.")

with tab_suppr:
    id_gare = st.number_input("ID de la gare", min_value=1, step=1)
    if st.button("Supprimer la gare"):
        res = api_client.delete(f"/gares/{int(id_gare)}")
        if afficher_resultat(res, "Gare supprimée."):
            logger.info(f"Gare supprimée : {id_gare}")
