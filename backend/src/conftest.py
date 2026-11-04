import os

# Configuration de toutes les variables d'environnement requises par DBConnection
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_DATABASE"] = "test_db"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "postgres"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_SCHEMA"] = "public"
os.environ["SNCF_API_KEY"] = "fake_key"