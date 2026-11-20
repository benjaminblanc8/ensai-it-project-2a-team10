import logging
import os

import requests
import streamlit as st
from utils.env_variables import load_environment_variables

# Chargé ici aussi : une page ouverte directement n'est pas passée par app.py
load_environment_variables()

DEFAULT_TIMEOUT = int(os.getenv("BACKEND_TIMEOUT", 5))
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class APIClient:
    """Client HTTP vers le backend FastAPI (ajoute automatiquement le token JWT).

    Chaque méthode renvoie {"status_code": int, "data": ...}.
    status_code vaut 0 en cas d'erreur réseau (timeout, backend éteint...).
    """

    def __init__(self, base_url: str, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _get_headers(self) -> dict:
        headers = {}
        token = st.session_state.get("access_token")
        if token:
            # FastAPI OAuth2PasswordBearer attend ce format
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        logger = st.session_state.get("logger") or logging.getLogger(__name__)
        logger.info(f"  {method} {url}")

        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())
        timeout = kwargs.pop("timeout", self.timeout)

        response = None
        data = None
        try:
            response = self.session.request(
                method=method, url=url, timeout=timeout, headers=headers, **kwargs
            )
            try:
                data = response.json()
            except Exception:
                data = response.text
            return {"status_code": response.status_code, "data": data}

        except requests.exceptions.Timeout:
            return {"status_code": 0, "data": "Le serveur ne répond pas (timeout)."}
        except requests.exceptions.ConnectionError:
            return {"status_code": 0, "data": f"Backend injoignable ({self.base_url})."}
        except requests.exceptions.RequestException as e:
            return {"status_code": 0, "data": str(e)}
        finally:
            if response is not None:
                logger.info(f"  {response.status_code} {response.reason}")
                logger.debug(f"  {data}")

    def get(self, path: str, params=None, **kwargs):
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path: str, json=None, data=None, **kwargs):
        return self._request("POST", path, json=json, data=data, **kwargs)

    def put(self, path: str, json=None, data=None, **kwargs):
        return self._request("PUT", path, json=json, data=data, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._request("DELETE", path, **kwargs)


api_client = APIClient(API_URL)
