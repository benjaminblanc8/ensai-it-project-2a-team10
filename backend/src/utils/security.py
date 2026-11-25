import os
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv
from jose import jwt

load_dotenv()
SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7


def create_access_token(utilisateur_id: int) -> str:
    """Crée un token d'accès JWT pour un utilisateur donné."""

    expiration = datetime.now(UTC) + timedelta(days=TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(utilisateur_id),
        "exp": expiration,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """Décode un token d'accès JWT et retourne le payload."""

    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )
