import os

import requests
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

API_KEY = os.getenv("SNCF_API_KEY")

if not API_KEY:
    raise RuntimeError("SNCF_API_KEY is missing. Add it to your .env file.")

BASE_URL = "https://api.sncf.com/v1/coverage/sncf/"


class ApiSncfService:
    def __init__(self):
        self.base_url = BASE_URL

    def obtenir_tout_les_arrets(
        self,
    ):  # à titre d'exemple, on ne peut pas récupérer toutes les gares
        url = f"{BASE_URL}stop_areas/"

        reponse = requests.get(url, auth=(API_KEY, ""))

        reponse.raise_for_status()

        data = reponse.json()

        if reponse.status_code == 200:
            return data
        else:
            reponse.raise_for_status()

    def obtenir_arrets_par_nom(
        self, name
    ):  # méthode qui permet de récupérer les gares/arrêts par nom
        url = f"{BASE_URL}places"

        params = {"q": name, "type[]": "stop_area"}

        reponse = requests.get(url, params=params, auth=(API_KEY, ""))

        reponse.raise_for_status()

        return reponse.json()


# Pour obtenir une gare avec un nom précis, on peut utiliser l'endpoint "places" avec le paramètre de requête "q" pour spécifier le nom de la gare. Par exemple, pour obtenir des informations sur la gare d'Abancourt, on peut faire une requête GET à l'URL suivante :
# https://api.sncf.com/v1/coverage/sncf/places?q=Abancourt&type[]=stop_area
