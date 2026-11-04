"""
Point d'entrée du service web FastAPI pour le projet Trajecto.

Initialise la journalisation, charge les variables d'environnement
et configure les routeurs de l'API (utilisateurs, gares, lignes, trajets, connexion).
"""

from controller import (
    connexion_controller,
    gare_controller,
    ligne_controller,
    trajet_controller,
    utilisateur_controller,
)
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from utils.env_variables import display_values, load_environment_variables
from utils.log_utils import LogMiddleware, get_logger, initialize_logs

# Initialisation
initialize_logs("Webservice")
load_environment_variables()
display_values()

logger = get_logger(__name__)

app = FastAPI(title="Trajecto")

app.add_middleware(LogMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Intercepte les erreurs de validation Pydantic (HTTP 422)
    et les enregistre dans les logs.
    """
    body = await request.body()
    body_str = body.decode("utf-8", errors="replace") if body else "empty body"

    errors = jsonable_encoder(exc.errors())

    logger.error(
        "Validation Error\nErrors: %s\nBody: %s",
        errors,
        body_str,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "body": body_str,
        },
    )


# Enregistrement des routeurs
app.include_router(
    utilisateur_controller.router,
    prefix="/utilisateur",
    tags=["Utilisateurs"],
)

app.include_router(
    connexion_controller.router,
    prefix="/connexion",
    tags=["Connexion"],
)

app.include_router(
    trajet_controller.router,
    prefix="/trajet",
    tags=["Trajets"],
)

app.include_router(
    gare_controller.router,
    prefix="/gare",
    tags=["Gares"],
)

app.include_router(
    ligne_controller.router,
    prefix="/ligne",
    tags=["Lignes"],
)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirige vers la documentation Swagger."""
    return RedirectResponse(url="/docs")


@app.get("/hello/{name}", tags=["Misc"])
async def hello_name(name: str):
    """Affiche un message Hello."""
    logger.info("Display Hello")
    return {"message": f"Hello {name}"}


# Lancement du serveur
if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("UVICORN_HOST", "127.0.0.1"),
        port=int(os.getenv("UVICORN_PORT", "5000")),
    )

    logger.info("Webservice stopped")
