import os
from datetime import datetime, timedelta, timezone

from jose import jwt

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7


def create_access_token(utilisateur_id: int) -> str:
    """Crée un JWT pour un utilisateur."""

    expiration = datetime.now(timezone.utc) + timedelta(
        days=TOKEN_EXPIRE_DAYS
    )

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
    """Décode et vérifie un JWT."""

    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )