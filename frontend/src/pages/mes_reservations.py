import pandas as pd
import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin
from utils.helpers import afficher_erreur, afficher_resultat
from utils.page_setup import setup_page

logger = setup_page("mes_reservations", "Mes réservations", min_level="CLIENT")

st.title("Mes réservations")

res = api_client.get(chemin("reservations", "/mes-reservations"))

if res["status_code"] != 200:
    afficher_erreur(res)
elif not res["data"]:
    st.info("Tu n'as aucune réservation. Va dans « Rechercher un trajet » pour en faire une.")
else:
    df = pd.json_normalize(res["data"])
    # Inutile (et potentiellement sensible) d'afficher les infos du compte
    df = df.drop(columns=[c for c in df.columns if c.startswith("utilisateur")])
    df = df.drop(columns=[c for c in df.columns if c.endswith("id_gare_sncf")])
    premieres = [c for c in ("id_reservation",) if c in df.columns]
    df = df[premieres + [c for c in df.columns if c not in premieres]]
    st.dataframe(df, hide_index=True)

    st.subheader("Annuler une réservation")
    if "id_reservation" not in df.columns:
        st.warning("Colonne id_reservation absente de la réponse de l'API.")
    else:
        choix = st.selectbox("Réservation", df["id_reservation"].tolist())
        if st.button("Annuler cette réservation"):
            res = api_client.delete(chemin("reservations", f"/{int(choix)}"))
            if afficher_resultat(res, "Réservation annulée, la place est libérée."):
                logger.info(f"Annulation de la réservation {choix}")
                st.rerun()
