import pandas as pd
import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin
from utils.helpers import afficher_erreur, afficher_resultat
from utils.page_setup import setup_page

logger = setup_page("gestion_lignes", "Gestion des lignes", min_level="COLLAB")

st.title("Lignes")
st.caption(
    "Une ligne relie deux gares dans un sens précis (A → B et B → A sont deux lignes). "
    "Les deux gares doivent être différentes et la liaison ne peut pas exister deux fois. "
    "Une ligne ne peut pas être supprimée si des trajets l'utilisent."
)

tab_liste, tab_creer, tab_voir, tab_modif, tab_suppr = st.tabs(
    ["Liste", "Créer", "Consulter", "Modifier", "Supprimer"]
)

with tab_liste:
    if st.button("Afficher toutes les lignes"):
        res = api_client.get(chemin("lignes", "/"))
        if res["status_code"] == 200:
            st.dataframe(pd.json_normalize(res["data"]), hide_index=True)
        else:
            afficher_erreur(res)

with tab_creer:
    with st.form("ligne_creation"):
        depart = st.text_input("Gare de départ (nom exact)")
        arrivee = st.text_input("Gare d'arrivée (nom exact)")
        creer = st.form_submit_button("Créer la ligne")
    if creer:
        res = api_client.post(
            chemin("lignes", "/"),
            json={"nom_gare_depart": depart, "nom_gare_arrivee": arrivee},
        )
        if afficher_resultat(res, "Ligne créée."):
            logger.info(f"Ligne créée : {depart} -> {arrivee}")
            st.json(res["data"])

with tab_voir:
    id_voir = st.number_input("ID de la ligne", min_value=1, step=1, key="ligne_voir")
    if st.button("Afficher la ligne"):
        res = api_client.get(chemin("lignes", f"/{int(id_voir)}"))
        if res["status_code"] == 200:
            st.json(res["data"])
        else:
            afficher_erreur(res)

with tab_modif:
    with st.form("ligne_modification"):
        id_modif = st.number_input("ID de la ligne", min_value=1, step=1)
        id_dep = st.number_input("ID gare de départ", min_value=1, step=1)
        id_arr = st.number_input("ID gare d'arrivée", min_value=1, step=1)
        modifier = st.form_submit_button("Modifier la ligne")
    if modifier:
        res = api_client.put(
            chemin("lignes", f"/{int(id_modif)}"),
            json={
                "id_ligne": int(id_modif),
                "id_gare_depart": int(id_dep),
                "id_gare_arrivee": int(id_arr),
            },
        )
        if afficher_resultat(res, "Ligne modifiée."):
            st.json(res["data"])

with tab_suppr:
    id_suppr = st.number_input("ID de la ligne", min_value=1, step=1, key="ligne_suppr")
    if st.button("Supprimer la ligne"):
        res = api_client.delete(chemin("lignes", f"/{int(id_suppr)}"))
        if afficher_resultat(res, "Ligne supprimée."):
            logger.info(f"Ligne supprimée : {id_suppr}")
