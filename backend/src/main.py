"""
Main entry point for the FastAPI web service.

Initializes logging, loads environment variables, and sets up API routers
for players, login, and games.
"""

from controller import (
    connexion_controller,
    gare_controller,
    ligne_controller,
    trajet_controller,
    utilisateur_controller,
)
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from utils.env_variables import display_values, load_environment_variables
from utils.log_utils import LogMiddleware, get_logger, initialize_logs

logger = get_logger(__name__)

# Initialization
initialize_logs("Webservice")

load_environment_variables()
display_values()


app = FastAPI(title="My Webservice")

app.add_middleware(LogMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Intercepts Pydantic 422 errors to log them.
    """
    body = await request.body()
    body_str = body.decode() if body else "empty body"

    logger.error(f"Validation Error\nErrors: {exc.errors()}\nBody: {body_str}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body_str},
    )


app.include_router(
    utilisateur_controller.router, prefix="/utilisateur", tags=["Utilisateurs"]
)
app.include_router(connexion_controller.router, prefix="/connexion", tags=["Connexion"])
app.include_router(trajet_controller.router, prefix="/trajet", tags=["Trajets"])
app.include_router(gare_controller.router, prefix="/gare", tags=["Gares"])
app.include_router(ligne_controller.router, prefix="/ligne", tags=["Lignes"])


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/docs")


@app.get("/hello/{name}", tags=["Misc"])
async def hello_name(name: str):
    """Display Hello"""
    logger.info("Display Hello")
    return {"message": f"Hello {name}"}


# Run the FastAPI application
if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("UVICORN_HOST", "127.0.0.1"),
        port=int(os.getenv("UVICORN_PORT", "5000")),
    )

    logger.info("Webservice stopped")
