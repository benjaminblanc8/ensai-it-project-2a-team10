import streamlit as st
from utils.auth_guard import check_authentification
from utils.env_variables import display_values, load_environment_variables
from utils.log_init import get_page_logger, initialize_logs
from utils.sidebar import render_sidebar


def setup_page(
    name: str,
    title: str,
    public: bool = False,
    min_level: str | None = None,
):
    """À appeler en première ligne de chaque page.

    Configure la page, initialise les logs une seule fois, affiche le menu
    puis vérifie la connexion et le rôle. Retourne le logger de la page.
    """
    st.set_page_config(page_title=title, page_icon="🚆", layout="wide")

    if "logs_initialized" not in st.session_state:
        initialize_logs("Streamlit App")
        load_environment_variables()
        display_values(include_prefix="BACKEND")
        st.session_state["logs_initialized"] = True

    logger = get_page_logger(name)

    render_sidebar()
    if not public:
        check_authentification(min_level)

    return logger
