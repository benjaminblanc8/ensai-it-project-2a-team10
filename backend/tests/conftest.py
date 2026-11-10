import os
from unittest.mock import MagicMock

# Neutralisation totale de la base de données et des clés pour tous les tests
import dao.db_connection

dao.db_connection.DBConnection = MagicMock()

os.environ["JWT_SECRET_KEY"] = "fake_jwt_secret_key_for_tests"
os.environ["SNCF_API_KEY"] = "fake_sncf_api_key_for_tests"
