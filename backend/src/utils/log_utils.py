
import inspect
import logging
import logging.config
import numbers
import time
from contextvars import ContextVar
from functools import wraps
from pathlib import Path
from typing import Any

import yaml
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

_INDENTATION: ContextVar[int] = ContextVar(
    "log_indentation",
    default=0,
)

INDENTATION_SIZE = 2
MAX_STRING_LENGTH = 100
MAX_COLLECTION_ITEMS = 3

SENSITIVE_KEYWORDS = {
    "password",
    "passwd",
    "pwd",
    "pass",
    "token",
    "secret",
    "authorization",
    "api_key",
    "private_key",
    "credential",
    "mdp",
}

logger = logging.getLogger(__name__)


def initialize_logs(name: str) -> None:
    """Initialise la journalisation à partir du fichier YAML."""

    project_root = Path(__file__).resolve().parents[2]

    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    config_file = project_root / "logging_config.yml"

    if not config_file.is_file():
        raise FileNotFoundError(
            f"Fichier de configuration des logs introuvable : "
            f"{config_file}"
        )

    with config_file.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    if not isinstance(config, dict):
        raise ValueError(
            "La configuration YAML des logs doit être un dictionnaire."
        )

    logging.config.dictConfig(config)

    app_logger = logging.getLogger(name)

    app_logger.info("-" * 50)
    app_logger.info("Démarrage de %s", name)
    app_logger.info("-" * 50)


# ---------------------------------------------------------------------
# Logger management
# ---------------------------------------------------------------------

def get_logger(module_name: str, max_size: int = 25) -> logging.Logger:
    """
    Renvoie un logger avec un nom raccourci basé sur le module.

    Si le nom dépasse max_size, les parties intermédiaires
    sont remplacées par leurs initiales.
    """

    if max_size < 1:
        raise ValueError("max_size doit être supérieur à zéro.")

    if len(module_name) <= max_size:
        return logging.getLogger(module_name)

    parts = module_name.split(".")

    if len(parts) == 1:
        return logging.getLogger(module_name[:max_size])

    short_name = ".".join(
        [part[0] for part in parts[:-1]] + [parts[-1]]
    )

    return logging.getLogger(short_name)


# ---------------------------------------------------------------------
# Indentation management
# ---------------------------------------------------------------------

class LogIndentation:
    """Gère l'indentation des logs par contexte d'exécution."""

    @classmethod
    def increase_indentation(cls):
        """Augmente l'indentation du contexte actuel."""

        _INDENTATION.set(_INDENTATION.get() + 1)

    @classmethod
    def decrease_indentation(cls):
        """Diminue l'indentation sans passer sous zéro."""

        _INDENTATION.set(max(0, _INDENTATION.get() - 1))

    @classmethod
    def get_indentation(cls) -> str:
        """Renvoie l'indentation actuelle."""

        return " " * INDENTATION_SIZE * _INDENTATION.get()


# ---------------------------------------------------------------------
# Safe value formatting
# ---------------------------------------------------------------------

def _is_sensitive(name: str) -> bool:
    """Détermine si un nom de paramètre est sensible."""

    normalized = name.lower().replace("-", "_")

    return any(
        keyword in normalized
        for keyword in SENSITIVE_KEYWORDS
    )


def _format_value(
    value: Any,
    depth: int = 0,
) -> str:
    """
    Formate une valeur sans exposer directement les attributs
    internes des objets.

    Les collections sont limitées en taille et en profondeur.
    """

    if value is None:
        return "None"

    if isinstance(value, bool):
        return str(value)

    if isinstance(value, numbers.Number):
        return str(value)

    if isinstance(value, str):
        if len(value) > MAX_STRING_LENGTH:
            return (
                repr(value[:MAX_STRING_LENGTH])
                + f"... ({len(value)} caractères)"
            )
        return repr(value)

    if depth >= 2:
        return f"<{type(value).__name__}>"

    if isinstance(value, dict):
        items = []

        for key, item in list(value.items())[:MAX_COLLECTION_ITEMS]:
            key_str = str(key)

            if _is_sensitive(key_str):
                item_str = "*****"
            else:
                item_str = _format_value(item, depth + 1)

            items.append(f"{key_str}: {item_str}")

        if len(value) > MAX_COLLECTION_ITEMS:
            items.append(f"... ({len(value)} éléments)")

        return "{" + ", ".join(items) + "}"

    if isinstance(value, (list, tuple, set)):
        items = [
            _format_value(item, depth + 1)
            for item in list(value)[:MAX_COLLECTION_ITEMS]
        ]

        if len(value) > MAX_COLLECTION_ITEMS:
            items.append(f"... ({len(value)} éléments)")

        return "[" + ", ".join(items) + "]"

    return f"<{type(value).__name__}>"


def _format_arguments(func, args, kwargs) -> str:
    """Formate les arguments en masquant les paramètres sensibles."""

    try:
        signature = inspect.signature(func)
        bound = signature.bind_partial(*args, **kwargs)

        arguments = []

        for name, value in bound.arguments.items():

            # Ne pas journaliser l'instance de la classe.
            if name in {"self", "cls"}:
                continue

            if _is_sensitive(name):
                formatted_value = "*****"
            else:
                formatted_value = _format_value(value)

            arguments.append(f"{name}={formatted_value}")

        return "(" + ", ".join(arguments) + ")"

    except (TypeError, ValueError):
        # En cas de problème d'inspection, ne pas exposer
        # les arguments bruts.
        return "(arguments non disponibles)"


def _format_output(result: Any) -> str:
    """Formate la valeur de retour d'une méthode."""

    return _format_value(result)


# ---------------------------------------------------------------------
# Logging decorator
# ---------------------------------------------------------------------

def log(func):
    """
    Décorateur de journalisation compatible avec les fonctions
    synchrones et asynchrones.

    Journalise :
    - L'entrée dans la méthode.
    - Les arguments non sensibles.
    - La durée d'exécution.
    - La valeur de retour.
    - Les exceptions éventuelles.
    """

    method_name = func.__qualname__
    method_logger = get_logger(func.__module__)
    is_async = inspect.iscoroutinefunction(func)

    if is_async:

        @wraps(func)
        async def async_wrapper(*args, **kwargs):

            indentation_token = _INDENTATION.set(
                _INDENTATION.get() + 1
            )

            indentation = LogIndentation.get_indentation()
            arguments = _format_arguments(func, args, kwargs)
            start_time = time.perf_counter()

            try:
                method_logger.info(
                    "%s%s%s - START",
                    indentation,
                    method_name,
                    arguments,
                )

                result = await func(*args, **kwargs)

                elapsed = time.perf_counter() - start_time

                method_logger.info(
                    "%s%s - END (%.3fs)",
                    indentation,
                    method_name,
                    elapsed,
                )

                method_logger.info(
                    "%s  └─> Output: %s",
                    indentation,
                    _format_output(result),
                )

                return result

            except Exception:
                method_logger.exception(
                    "%s%s - FAILED",
                    indentation,
                    method_name,
                )
                raise

            finally:
                _INDENTATION.reset(indentation_token)

        return async_wrapper

    @wraps(func)
    def wrapper(*args, **kwargs):

        indentation_token = _INDENTATION.set(
            _INDENTATION.get() + 1
        )

        indentation = LogIndentation.get_indentation()
        arguments = _format_arguments(func, args, kwargs)
        start_time = time.perf_counter()

        try:
            method_logger.info(
                "%s%s%s - START",
                indentation,
                method_name,
                arguments,
            )

            result = func(*args, **kwargs)

            elapsed = time.perf_counter() - start_time

            method_logger.info(
                "%s%s - END (%.3fs)",
                indentation,
                method_name,
                elapsed,
            )

            method_logger.info(
                "%s  └─> Output: %s",
                indentation,
                _format_output(result),
            )

            return result

        except Exception:
            method_logger.exception(
                "%s%s - FAILED",
                indentation,
                method_name,
            )
            raise

        finally:
            _INDENTATION.reset(indentation_token)

    return wrapper


# ---------------------------------------------------------------------
# HTTP middleware
# ---------------------------------------------------------------------

class LogMiddleware(BaseHTTPMiddleware):
    """Journalise les requêtes HTTP et leurs réponses."""

    async def dispatch(self, request: Request, call_next):

        method = request.method
        path = request.url.path

        request_logger = logging.getLogger("app.http")

        start_time = time.perf_counter()

        request_logger.info(
            "%s %s - START",
            method,
            path,
        )

        try:
            response = await call_next(request)

            elapsed = time.perf_counter() - start_time

            request_logger.info(
                "%s %s - END [Status: %s] (%.3fs)",
                method,
                path,
                response.status_code,
                elapsed,
            )

            return response

        except Exception:
            elapsed = time.perf_counter() - start_time

            request_logger.exception(
                "%s %s - FAILED (%.3fs)",
                method,
                path,
                elapsed,
            )

            raise
