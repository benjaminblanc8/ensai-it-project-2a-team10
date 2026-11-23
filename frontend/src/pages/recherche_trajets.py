import pandas as pd
import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin
from utils.helpers import (
    afficher_erreur,
    afficher_resultat,
    libelle_trajet,
    trajets_dataframe,
)
from utils.page_setup import setup_page
from utils.selecteur_gare import selecteur_gare

# Recherche publique (cahier des charges 3.4) : pas besoin d'être connecté
logger = setup_page("recherche_trajets", "Rechercher un trajet", public=True)

st.title("Rechercher un trajet")
st.caption(
    "Seuls les trajets enregistrés par les collaborateurs sont proposés, "
    "dans le sens demandé."
)

with st.expander("Lignes disponibles"):
    res_lignes = api_client.get(chemin("lignes", "/"))
    if res_lignes["status_code"] == 200 and res_lignes["data"]:
        st.dataframe(pd.json_normalize(res_lignes["data"]), hide_index=True)
    else:
        st.caption("Liste des lignes indisponible.")

with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        depart = selecteur_gare("Gare de départ", key="sel_depart", source="sncf")
    with c2:
        arrivee = selecteur_gare("Gare d'arrivée", key="sel_arrivee", source="sncf")
    chercher = st.button("Rechercher", type="primary")

if chercher:
    if not depart.strip() or not arrivee.strip():
        st.warning("Renseigne les deux gares.")
    elif depart.strip().casefold() == arrivee.strip().casefold():
        st.warning("Les gares de départ et d'arrivée doivent être différentes.")
    else:
        # Les deux couples de noms de paramètres sont envoyés (cahier des charges
        # et contrôleur) ; FastAPI ignore ceux qu'il ne connaît pas.
        res = api_client.get(
            chemin("trajets", "/"),
            params={
                "gare_depart": depart,
                "gare_arrivee": arrivee,
                "nom_gare_depart": depart,
                "nom_gare_arrivee": arrivee,
            },
        )
        if res["status_code"] == 200:
            st.session_state["resultats_trajets"] = res["data"]
        else:
            st.session_state["resultats_trajets"] = None
            afficher_erreur(res)

trajets = st.session_state.get("resultats_trajets")

if trajets is None:
    st.info("Saisis deux gares pour afficher les trajets disponibles.")
elif not trajets:
    st.info("Aucun trajet ne correspond à cette recherche.")
else:
    df = trajets_dataframe(trajets)
    st.dataframe(df, hide_index=True)

    st.subheader("Réserver")
    if not st.session_state.get("access_token"):
        st.info("Connecte-toi (page « Connexion / inscription ») pour réserver.")
    else:
        if "places_disponibles" in df.columns:
            disponibles = df[df["places_disponibles"] > 0]
        else:
            disponibles = df
        if disponibles.empty:
            st.warning("Tous ces trajets sont complets.")
        else:
            libelles = {int(r["id_trajet"]): libelle_trajet(r) for _, r in disponibles.iterrows()}
            choix = st.selectbox("Trajet", list(libelles), format_func=libelles.get)
            if st.button("Réserver ce trajet", type="primary"):
                res = api_client.post(chemin("reservations", "/"), json={"id_trajet": int(choix)})
                if afficher_resultat(res, "Réservation effectuée."):
                    logger.info(f"Réservation du trajet {choix}")
                    st.session_state["resultats_trajets"] = None  # rafraîchit les places
