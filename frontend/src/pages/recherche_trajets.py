import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin
from utils.helpers import afficher_erreur, afficher_resultat, trajets_dataframe
from utils.page_setup import setup_page

logger = setup_page("recherche_trajets", "Rechercher un trajet", min_level="CLIENT")

st.title("Rechercher un trajet")

with st.form("recherche"):
    c1, c2 = st.columns(2)
    depart = c1.text_input("Gare de départ", placeholder="Paris Montparnasse")
    arrivee = c2.text_input("Gare d'arrivée", placeholder="Rennes")
    chercher = st.form_submit_button("Rechercher")

if chercher:
    res = api_client.get(
        chemin("trajets", "/"),
        params={"nom_gare_depart": depart, "nom_gare_arrivee": arrivee},
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
    st.info("Aucun trajet entre ces gares. Vérifie l'orthographe exacte des noms.")
else:
    df = trajets_dataframe(trajets)
    st.dataframe(df, hide_index=True)

    st.subheader("Réserver")
    disponibles = df[df["places_disponibles"] > 0]
    if disponibles.empty:
        st.warning("Tous ces trajets sont complets.")
    else:
        libelles = {
            int(r.id_trajet): (
                f"#{r.id_trajet} — {r.date_heure_depart:%d/%m/%Y %H:%M} — "
                f"{r.tarif} € — {r.places_disponibles} place(s)"
            )
            for r in disponibles.itertuples()
        }
        choix = st.selectbox("Trajet", list(libelles), format_func=libelles.get)
        if st.button("Réserver ce trajet", type="primary"):
            res = api_client.post(chemin("reservations", "/"), json={"id_trajet": int(choix)})
            if afficher_resultat(res, "Réservation effectuée."):
                logger.info(f"Réservation du trajet {choix}")
                st.session_state["resultats_trajets"] = None  # rafraîchit les places
