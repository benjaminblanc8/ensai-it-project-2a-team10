"""Point d'entrée : redirige vers l'accueil ou le menu.

Lancer depuis le dossier frontend/ :  streamlit run src/app.py
"""

import streamlit as st

if st.session_state.get("access_token"):
    st.switch_page("pages/menu.py")
else:
    st.switch_page("pages/home.py")
