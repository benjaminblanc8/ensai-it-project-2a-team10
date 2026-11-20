from datetime import date, datetime, time, timedelta

import pandas as pd
import streamlit as st
from utils.sidebar import deconnecter


def message_erreur(res: dict) -> str:
    """Transforme une réponse d'erreur FastAPI en texte lisible."""
    data = res["data"]
    if isinstance(data, dict):
        detail = data.get("detail", data)
        if isinstance(detail, list):  # erreurs de validation 422
            return " ; ".join(
                f"{'.'.join(str(x) for x in d.get('loc', [])[1:])} : {d.get('msg')}"
                for d in detail
            )
        return str(detail)
    return str(data)


def afficher_erreur(res: dict):
    """Affiche l'erreur ; si le token a expiré, déconnecte et renvoie à l'accueil."""
    if res["status_code"] == 401 and st.session_state.get("access_token"):
        deconnecter()
        st.warning("Session expirée, reconnecte-toi.")
        st.switch_page("pages/home.py")
    prefixe = f"{res['status_code']} — " if res["status_code"] else ""
    st.error(f"{prefixe}{message_erreur(res)}")


def afficher_resultat(res: dict, succes: str) -> bool:
    """Affiche un succès ou l'erreur. Retourne True si la requête a réussi."""
    if res["status_code"] in (200, 201):
        st.success(succes)
        return True
    afficher_erreur(res)
    return False


def trajets_dataframe(trajets: list) -> pd.DataFrame:
    """Met en forme la liste de TrajetReadModel pour l'affichage."""
    df = pd.DataFrame(trajets)
    if df.empty:
        return df
    df["date_heure_depart"] = pd.to_datetime(df["date_heure_depart"])
    df["arrivee_estimee"] = df["date_heure_depart"] + pd.to_timedelta(
        df["duree_minutes"], unit="m"
    )
    return df[
        [
            "id_trajet",
            "date_heure_depart",
            "arrivee_estimee",
            "duree_minutes",
            "tarif",
            "places_disponibles",
            "places_reservees",
            "nb_places",
            "id_ligne",
        ]
    ]


def saisie_horaire(prefix: str) -> datetime:
    """Sélecteurs de date et d'heure, retourne un datetime."""
    defaut = datetime.now() + timedelta(days=1)
    c1, c2 = st.columns(2)
    jour = c1.date_input(
        "Date de départ", defaut.date(), min_value=date.today(), key=f"{prefix}_date"
    )
    heure = c2.time_input(
        "Heure de départ", time(defaut.hour, 0), key=f"{prefix}_heure"
    )
    return datetime.combine(jour, heure)
