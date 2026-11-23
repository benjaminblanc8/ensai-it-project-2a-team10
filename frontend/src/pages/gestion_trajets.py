import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin
from utils.helpers import afficher_erreur, afficher_resultat, saisie_horaire
from utils.page_setup import setup_page
from utils.selecteur_gare import selecteur_gare

logger = setup_page("gestion_trajets", "Gestion des trajets", min_level="COLLAB")

st.title("Trajets")

tab_creer, tab_voir, tab_modif, tab_suppr = st.tabs(
    ["Créer", "Consulter", "Modifier", "Supprimer"]
)

with tab_creer:
    st.caption("La durée est calculée automatiquement par le backend via l'API SNCF.")

    c1, c2 = st.columns(2)
    with c1:
        depart = selecteur_gare("Gare de départ", key="tc_depart", source="base")
    with c2:
        arrivee = selecteur_gare("Gare d'arrivée", key="tc_arrivee", source="base")

    horaire = saisie_horaire("tc")

    c1, c2 = st.columns(2)
    places = c1.number_input("Nombre de places", min_value=1, value=100, step=1, key="tc_places")
    tarif = c2.number_input("Tarif (€)", min_value=0.0, value=30.0, step=1.0, key="tc_tarif")

    if st.button("Créer le trajet", type="primary"):
        if not depart or not arrivee:
            st.warning("Choisis les deux gares dans les listes proposées.")
        else:
            res = api_client.post(
                chemin("trajets", "/"),
                json={
                    "nom_gare_depart": depart,
                    "nom_gare_arrivee": arrivee,
                    "date_heure_depart": horaire.isoformat(),
                    "nb_places": int(places),
                    "tarif": float(tarif),
                },
                timeout=60,  # l'appel à l'API SNCF peut être lent
            )
            if afficher_resultat(res, "Trajet créé."):
                logger.info(f"Trajet créé : {depart} -> {arrivee}")
                st.json(res["data"])

with tab_voir:
    id_voir = st.number_input("ID du trajet", min_value=1, step=1, key="tv_id")
    if st.button("Afficher le trajet"):
        res = api_client.get(chemin("trajets", f"/{int(id_voir)}"))
        if res["status_code"] == 200:
            st.json(res["data"])
        else:
            afficher_erreur(res)

with tab_modif:
    st.caption("La durée est recalculée si la date ou la ligne change.")
    id_modif = st.number_input("ID du trajet", min_value=1, step=1, key="tm_id")
    id_ligne = st.number_input("ID de la ligne", min_value=1, step=1, key="tm_ligne")
    horaire_m = saisie_horaire("tm")
    c1, c2 = st.columns(2)
    places_m = c1.number_input("Nombre de places", min_value=1, value=100, step=1, key="tm_places")
    tarif_m = c2.number_input("Tarif (€)", min_value=0.0, value=30.0, step=1.0, key="tm_tarif")

    if st.button("Enregistrer les modifications"):
        res = api_client.put(
            chemin("trajets", f"/{int(id_modif)}"),
            json={
                "id_ligne": int(id_ligne),
                "date_heure_depart": horaire_m.isoformat(),
                "nb_places": int(places_m),
                "tarif": float(tarif_m),
            },
            timeout=60,
        )
        if afficher_resultat(res, "Trajet modifié."):
            st.json(res["data"])

with tab_suppr:
    id_suppr = st.number_input("ID du trajet", min_value=1, step=1, key="ts_id")
    if st.button("Supprimer le trajet"):
        res = api_client.delete(chemin("trajets", f"/{int(id_suppr)}"))
        if afficher_resultat(res, "Trajet supprimé."):
            logger.info(f"Trajet supprimé : {id_suppr}")
