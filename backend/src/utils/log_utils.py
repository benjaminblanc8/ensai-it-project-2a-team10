import logging
import logging.config
import numbers
from functools import wraps
from pathlib import Path

import yaml
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


def initialize_logs(name: str):
    """Initialise la journalisation à partir d'un fichier de configuration."""

    # Crée le dossier logs à la racine du projet s'il n'existe pas
    logs_dir = Path(__file__).resolve().parents[2] / "logs"
    logs_dir.mkdir(exist_ok=True)

    config_file = Path(__file__).resolve().parents[2] / "logging_config.yml"

    with open(config_file, encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
        logging.config.dictConfig(config)

        logging.info("-" * 50)  # ruff: ignore[root-logger-call]
        logging.info(f"Démarrage de {name}                       ")  # ruff: ignore[root-logger-call]
        logging.info("-" * 50)  # ruff: ignore[root-logger-call]


def get_logger(module_name: str, max_size: int = 25):
    """
    Renvoie un logger avec un nom raccourci basé sur le chemin du module.
    Si le chemin dépasse max_size, utilise les initiales pour les parties préfixes.
    """
    if len(module_name) <= max_size:
        return logging.getLogger(module_name)

    parts = module_name.split(".")
    short_prefix = [p[0] for p in parts[:-1]]
    short_name = ".".join(short_prefix + [parts[-1]])

    return logging.getLogger(short_name)


class LogIndentation:
    """Gère l'indentation des logs lors de l'entrée dans une nouvelle méthode."""

    current_indentation = 0
    indentation_size = 2

    @classmethod
    def increase_indentation(cls):
        """Augmente l'indentation."""
        cls.current_indentation += 1

    @classmethod
    def decrease_indentation(cls):
        """Diminue l'indentation."""
        cls.current_indentation -= 1

    @classmethod
    def get_indentation(cls):
        """Renvoie l'indentation actuelle."""
        return " " * cls.indentation_size * cls.current_indentation


def log(func):
    """Décorateur pour journaliser les appels de méthodes et leurs sorties.

    Appliqué à une méthode, il journalise :
    - l'appel de la méthode avec les valeurs des paramètres

    - la valeur de retour de la méthode
    """

    SENSITIVE_KEYWORDS = {
        "password",
        "passwd",
        "pwd",
        "pass",
        "token",
        "secret",
        "key",
    }

    @wraps(func)
    def wrapper(*args, **kwargs):
        if args and hasattr(args[0], "__class__"):
            logger = get_logger(f"{args[0].__class__.__module__}")
        else:
            logger = logging.getLogger(__name__)

        LogIndentation.increase_indentation()
        indentation = LogIndentation.get_indentation()

        # Récupère les paramètres de la méthode
        method_name = func.__name__
        param_names = func.__code__.co_varnames[1 : func.__code__.co_argcount]
        args_list = []

        for i, arg in enumerate(args[1:]):
            if i >= len(param_names):
                break
            param_name = param_names[i].lower()
            if any(keyword in param_name for keyword in SENSITIVE_KEYWORDS):
                args_list.append("*****")
            else:
                args_list.append(
                    str(arg) if not isinstance(arg, numbers.Number) else arg
                )

        for k, v in kwargs.items():
            if any(keyword in k.lower() for keyword in SENSITIVE_KEYWORDS):
                args_list.append("*****")
            else:
                args_list.append(str(v) if not isinstance(v, numbers.Number) else v)

        args_tuple = tuple(args_list)

        # Journalise l'entrée dans la méthode
        logger.info(f"{indentation}{method_name}{args_tuple} - START")
        result = func(*args, **kwargs)
        logger.info(f"{indentation}{method_name}{args_tuple} - END")

        # Raccourcit les sorties longues pour la lisibilité
        if isinstance(result, list):
            result_str = str([str(item) for item in result[:3]])
            result_str += f" ... ({len(result)} elements)"
        elif isinstance(result, dict):
            result_str = [(str(k), str(v)) for k, v in list(result.items())[:3]]
            result_str += f" ... ({len(result)} elements)"
        elif isinstance(result, str) and len(result) > 50:
            result_str = result[:50] + f" ... ({len(result)} characters)"
        else:
            result_str = str(result)

        logger.info(f"{indentation}  └─> Output: {result_str}")

        LogIndentation.decrease_indentation()

        return result

    return wrapper


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """Middleware pour journaliser les requêtes et réponses HTTP.
        Capture la méthode, le chemin, le code de statut et les détails d'erreur."""

        method = request.method
        path = str(request.url.path)

        logging.info(f"{method} {path} - START")  # ruff: ignore[root-logger-call]

        try:
            response = await call_next(request)
            logging.info(f"{method} {path} - END [Status: {response.status_code}]")  # ruff: ignore[root-logger-call]
            return response

        except Exception as e:
            logging.error(f"{method} {path} - FAILED [Status: 500] Error: {e!s}")  # ruff: ignore[root-logger-call]
            raise
