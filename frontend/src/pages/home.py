import streamlit as st
from utils.api_client import api_client
from utils.endpoints import chemin, etat_routes, liste_routes
from utils.helpers import afficher_resultat, message_erreur
from utils.page_setup import setup_page

logger = setup_page("home", "Connexion", public=True)

st.title("🚆 Billets de train")
st.write("Recherche un trajet, réserve ta place et gère tes réservations.")

with st.expander("Diagnostic de l'API"):
    st.write(f"Backend : `{api_client.base_url}`")
    st.json(etat_routes())
    st.write("Routes exposées par le backend :")
    st.code("\n".join(liste_routes()) or "(/openapi.json indisponible)")

tab_login, tab_signup = st.tabs(["Se connecter", "Créer un compte"])

with tab_login:
    with st.form("login"):
        pseudo = st.text_input("Pseudo")
        mdp = st.text_input("Mot de passe", type="password")
        envoyer = st.form_submit_button("Se connecter")

    if envoyer:
        # OAuth2PasswordRequestForm attend des données de formulaire (pas du JSON)
        res = api_client.post(chemin("connexion", "/"), data={"username": pseudo, "password": mdp})

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
            me = api_client.get(chemin("utilisateurs", "/me"))
            if me["status_code"] == 200:
                st.session_state["pseudo"] = me["data"].get("pseudo", pseudo)
                donnees = me["data"]
                brut = next(
                    (donnees[k] for k in ("niveau", "habilitation", "niveau_habilitation", "role") if k in donnees),
                    None,
                )
                # "NiveauHabilitation.ADMIN" -> "ADMIN" ; valeur inconnue -> "INCONNU"
                niveau = str(getattr(brut, "name", brut)).split(".")[-1].upper()
                st.session_state["niveau"] = niveau if niveau in ("CLIENT", "COLLAB", "ADMIN") else "INCONNU"
                logger.info(f"Niveau détecté : {st.session_state['niveau']} (brut : {brut})")
            else:
                # Le JWT ne contient que l'id et l'expiration : sans route /me le rôle est inconnu
                st.session_state["niveau"] = "INCONNU"
                logger.warning("Route « utilisateur courant » indisponible : rôle inconnu")

            logger.info("Connexion réussie")
            st.switch_page("pages/menu.py")

with tab_signup:
    with st.form("signup"):
        pseudo_new = st.text_input("Pseudo", key="signup_pseudo")
        mdp_new = st.text_input("Mot de passe", type="password", key="signup_mdp")
        creer = st.form_submit_button("Créer le compte")

    if creer:
        corps = {"pseudo": pseudo_new, "mdp": mdp_new}
        res = api_client.post(chemin("inscription", "/"), json=corps)  # POST /inscription/
        if res["status_code"] in (404, 405):  # ancienne route POST /utilisateur(s)/
            res = api_client.post(chemin("utilisateurs", "/"), json=corps)
        afficher_resultat(res, "Compte créé (niveau CLIENT), tu peux te connecter.")
