import streamlit as st
from utils.api_client import api_client
from utils.helpers import afficher_resultat, message_erreur
from utils.page_setup import setup_page

logger = setup_page("home", "Connexion", public=True)

st.title("🚆 Billets de train")
st.write("Recherche un trajet, réserve ta place et gère tes réservations.")

tab_login, tab_signup = st.tabs(["Se connecter", "Créer un compte"])

with tab_login:
    with st.form("login"):
        pseudo = st.text_input("Pseudo")
        mdp = st.text_input("Mot de passe", type="password")
        envoyer = st.form_submit_button("Se connecter")

    if envoyer:
        # OAuth2PasswordRequestForm attend des données de formulaire (pas du JSON)
        res = api_client.post("/connexion/", data={"username": pseudo, "password": mdp})

        if res["status_code"] != 200:
            st.error(message_erreur(res))
        else:
            data = res["data"]
            token = data.get("access_token") if isinstance(data, dict) else data
            if not token:
                st.error(f"Réponse inattendue du serveur : {data}")
                st.stop()

            st.session_state["access_token"] = token
            st.session_state["pseudo"] = pseudo

            # Récupère le rôle (endpoint GET /utilisateurs/me à ajouter au backend)
            me = api_client.get("/utilisateurs/me")
            if me["status_code"] == 200:
                st.session_state["pseudo"] = me["data"].get("pseudo", pseudo)
                st.session_state["niveau"] = str(
                    me["data"].get("niveau", "CLIENT")
                ).upper()
            else:
                st.session_state["niveau"] = "CLIENT"
                logger.warning(
                    "GET /utilisateurs/me indisponible : rôle CLIENT par défaut"
                )

            logger.info("Connexion réussie")
            st.switch_page("pages/menu.py")

with tab_signup:
    with st.form("signup"):
        pseudo_new = st.text_input("Pseudo", key="signup_pseudo")
        mdp_new = st.text_input("Mot de passe", type="password", key="signup_mdp")
        creer = st.form_submit_button("Créer le compte")

    if creer:
        res = api_client.post(
            "/utilisateurs/", json={"pseudo": pseudo_new, "mdp": mdp_new}
        )
        afficher_resultat(res, "Compte créé, tu peux te connecter.")
