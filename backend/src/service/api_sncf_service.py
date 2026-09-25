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

    def get_stops(self):
        url = f"{BASE_URL}stop_points/"

        response = requests.get(url, auth=(API_KEY, ""))

        response.raise_for_status()

        data = response.json()

        if response.status_code == 200:
            return data
        else:
            response.raise_for_status()
