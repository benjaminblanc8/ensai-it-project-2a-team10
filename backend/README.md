# Backend — Trajecto API

The Trajecto backend is a layered REST API built with FastAPI. It handles railway stations, lines, journeys, user accounts, authentication, and PostgreSQL persistence.

For installation prerequisites, environment variables, and API usage examples, see the [main README](../README.md).

## 🚀 Development setup

From the repository root, install the backend dependencies, including development dependencies:

```bash
uv sync --project backend --all-extras
```

Then start the application from the backend directory:

```bash
cd backend
mkdir -p logs
uv run python src/main.py
```

Swagger is available at:

http://localhost:5000/docs

Run the application from `backend/` so that relative paths, including the log file path, resolve correctly.

## 🏛️ Architecture

The backend follows a layered architecture.

| Layer | Directory | Responsibility |
| --- | --- | --- |
| Business objects | `src/business_object/` | Domain entities such as Gare, Ligne, Trajet, Réservation and Utilisateur |
| Controllers | `src/controller/` | HTTP routes, dependency injection, and response construction |
| Services | `src/service/` | Business rules and coordination of DAO and SNCF operations |
| DAO | `src/dao/` | SQL queries, database transactions, and object reconstruction |
| Schemas | `src/schema/` | Pydantic request and response models |
| Utilities | `src/utils/` | Authentication, permission checks, configuration, and logging |

### Arborescence

```text
src/
├── main.py                         # Point d'entrée FastAPI, enregistrement des routeurs
├── business_object/
│   ├── gare.py                     # Entité Gare (id_gare, nom, ville, id_gare_sncf)
│   ├── ligne.py                    # Entité Ligne (relation entre deux gares)
│   ├── trajet.py                   # Entité Trajet (date, durée, places, tarif)
│   ├── reservation.py              # Entité Réservation
│   ├── utilisateur.py              # Entité Utilisateur (pseudo, mdp, habilitation)
│   └── niveau_habilitation.py      # Enum CLIENT / COLLAB / ADMIN
├── controller/
│   ├── api_sncf_controller.py      # Endpoints de recherche SNCF
│   ├── connexion_controller.py     # POST /connexion/ (login, obtention du token)
│   ├── gare_controller.py          # CRUD gares
│   ├── ligne_controller.py         # CRUD lignes
│   ├── reservation_controller.py   # CRUD réservations
│   ├── trajet_controller.py        # CRUD trajets
│   └── utilisateur_controller.py   # Création utilisateur, gestion des rôles
├── dao/
│   ├── db_connection.py            # Classe DBConnection (connexion PostgreSQL)
│   ├── gare_dao.py
│   ├── ligne_dao.py
│   ├── reservation_dao.py
│   ├── trajet_dao.py
│   └── utilisateur_dao.py
├── schema/
│   ├── gare_model.py               # Pydantic : GareCreationModel, GareReadModel, …
│   ├── ligne_model.py
│   ├── reservation_model.py
│   ├── trajet_model.py
│   └── utilisateur_model.py
├── service/
│   ├── api_sncf_service.py         # Client API SNCF (gares, itinéraires, durées)
│   ├── gare_service.py
│   ├── ligne_service.py
│   ├── reservation_service.py
│   ├── trajet_service.py
│   └── utilisateur_service.py
└── utils/
    ├── authentication.py           # Dépendance FastAPI : extraction du JWT
    ├── env_variables.py            # Chargement et affichage des variables .env
    ├── log_utils.py                # Initialisation du logging, @log, get_logger
    ├── security.py                 # Création et décodage des tokens JWT
    └── verification_habilitation.py # require_niveau() : contrôle d'accès
```

### Request processing

For a typical request:

1. FastAPI validates the input using a Pydantic schema.
2. The controller retrieves its dependencies and calls the service.
3. The service applies business rules and calls the DAO.
4. The DAO executes the SQL query and returns the result.
5. The controller returns data matching the response model.

Some operations also call the SNCF API through `ApiSncfService`.

### Exemple concret : création d'un trajet (`POST /trajet/`)

```
Client
  │
  ▼
TrajetCreationModel (schema/trajet_model.py)
  │  Pydantic valide : nom_gare_depart, nom_gare_arrivee, date_heure_depart, nb_places, tarif
  ▼
creer_trajet() (controller/trajet_controller.py)
  │  1. LigneService.rechercher_ligne_par_gares() → trouve la Ligne dans la BDD
  │  2. ApiSncfService().calculer_duree_trajet()  → interroge l'API SNCF
  │  3. ceil(duree.total_seconds() / 60)          → convertit en minutes entières (arrondi supérieur)
  │  4. TrajetService.creer_trajet()              → couche service
  ▼
TrajetService.creer_trajet() (service/trajet_service.py)
  │  Construit l'objet métier Trajet, appelle le DAO
  ▼
TrajetDao.creer_trajet() (dao/trajet_dao.py)
  │  INSERT INTO Trajet … RETURNING id_trajet
  │  commit() / rollback()
  ▼
Objet Trajet (business_object/trajet.py) avec id_trajet attribué
  │
  ▼
convertir_trajet() → TrajetReadModel (réponse JSON)
```

### Business objects and schemas

Business objects represent entities manipulated by the application.

Pydantic schemas define the API contract. Creation and modification schemas contain user-editable fields. Response schemas also expose generated values, such as database identifiers and calculated journey durations.

When changing a schema, check the corresponding controller, service, and response conversion.

### Conventions

- **Language**: identifiers, method names, class names, error messages, and docstrings are written in French. Use `snake_case` for functions and variables, `PascalCase` for classes.
- **Layer separation**: a controller never calls a DAO directly. A service contains no SQL. A DAO contains no business rules.
- **Business objects**: stored fields are private (underscore prefix), exposed through `@property` accessors named `get_*`. Example: `_nb_places` → `get_nb_places`.
- **Pydantic schemas**: `*CreationModel` contains only user-editable fields. `*ReadModel` adds generated identifiers and computed values (e.g. `places_disponibles`).
- **File naming**: `entity_controller.py`, `entity_service.py`, `entity_dao.py`, `entity_model.py` (e.g. `trajet_controller.py`, `trajet_service.py`, `trajet_dao.py`, `trajet_model.py`).

## 🗄️ Database access

Database connections are managed through `DBConnection` in:

```text
src/dao/db_connection.py
```

Connection settings are loaded from the `.env` file in the repository root:

| Variable | Description |
| --- | --- |
| `POSTGRES_HOST` | PostgreSQL server host |
| `POSTGRES_PORT` | PostgreSQL port (5432) |
| `POSTGRES_DATABASE` | Database name |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_SCHEMA` | PostgreSQL schema (e.g. `public`) |
| `UVICORN_HOST` | Server host (e.g. `0.0.0.0`) |
| `UVICORN_PORT` | Server port (e.g. `5000`) |
| `JWT_SECRET_KEY` | Secret key for JWT tokens |
| `SNCF_API_KEY` | SNCF API key (required for journey duration) |

DAO methods are responsible for parameterized SQL queries and transaction handling.

For write operations:

- Execute the query and commit using the same connection.
- Roll back the transaction if an error occurs.
- Close connections when the operation finishes.

Use SQL parameters for values:

```python
cursor.execute(
    "SELECT * FROM Trajet WHERE id_trajet = %s",
    (id_trajet,),
)
```

When modifying the data model, update the PostgreSQL schema, business objects, DAO queries, and API schemas together.

### Database schema

```text
Gare                         Ligne                        Trajet                      Réservation                  Utilisateur
────                         ─────                        ──────                      ───────────                  ───────────
id_gare (PK)                 id_ligne (PK)                id_trajet (PK)                id_reservation (PK)          id_utilisateur (PK)
nom                          id_gare_depart (FK → Gare)   date_heure_depart             id_trajet (FK → Trajet)    pseudo (UNIQUE)
ville                         id_gare_arrivee (FK → Gare)  duree_minutes                 id_utilisateur (FK)          mdp (hash)
id_gare_sncf                  date_creation                id_ligne (FK → Ligne)         habilitation (int)
                                                                      nb_places
                                                                      tarif
                                                                      places_reservees
```

A `Ligne` connects two `Gare` records (departure and arrival). A `Trajet` belongs to one `Ligne` and tracks seat availability. A `Réservation` links one `Utilisateur` to one `Trajet`.

A visual version of the schema is available at [`Diagrammes/diagramme_bdd.png`](../Diagrammes/diagramme_bdd.png).

## 🚆 SNCF integration

`src/service/api_sncf_service.py` centralizes requests to the SNCF API.

It provides station searches and journey calculations.

### Station identifiers

Stations have two identifiers:

| Identifier | Purpose |
| --- | --- |
| `id_gare` | Local PostgreSQL identifier used by application relationships |
| `id_gare_sncf` | SNCF identifier used for external API requests |

When creating a station, the service searches the SNCF API and stores the matching SNCF identifier.

### Journey duration

`calculer_duree_trajet()` receives the SNCF identifiers of the departure and arrival stations, together with the requested departure datetime.

It selects the shortest itinerary among the returned candidates containing public transport. It returns departure and arrival datetimes and a `timedelta` duration, or `None` when no suitable itinerary is found.

Journey creation converts the duration to minutes, rounding upward.

Journey modification recalculates the duration when the departure datetime or line changes.

The application retains the departure datetime entered by the user.

The SNCF API excludes non-rail transport modes (bus, tram, metro, coach) to return train-only itineraries.

**Pitfalls**:

- Do not confuse `id_gare` (local database key) with `id_gare_sncf` (external API key, e.g. `stop_area:SNCF:87471003`). SQL queries use `id_gare`; SNCF API calls use `id_gare_sncf`.
- Journey duration is stored as whole minutes (rounded up from seconds). Always use `ceil(duration.total_seconds() / 60)` when converting.
- If the SNCF API is unreachable or returns an error, the controller raises a `502`. If no train itinerary exists, it raises a `422`. Do not silently fall back to a default duration.

## 🔐 Authentication and permissions

JWT creation and decoding are implemented in:

```text
src/utils/security.py
```

The authenticated user is retrieved through:

```text
src/utils/authentication.py
```

Permission checks are implemented in:

```text
src/utils/verification_habilitation.py
```

Controllers use the `require_niveau()` dependency to enforce a minimum permission level.

```python
utilisateur = Depends(require_niveau(NiveauHabilitation.COLLAB))
```

Permission levels are ordered:

| Level | Value |
| --- | --- |
| CLIENT | 1 |
| COLLAB | 2 |
| ADMIN | 3 |

An administrator therefore satisfies a collaborator-level requirement.

## 📝 Logging

Logging is configured in:

```text
backend/logging_config.yml
```

When the server runs from `backend/`, logs are written to:

```text
backend/logs/backend.log
```

The configuration rotates the log file at midnight.

Use the project logger in application modules:

```python
from utils.log_utils import get_logger

logger = get_logger(__name__)

logger.info("Trajet créé : %s", trajet.id_trajet)
```

The `@log` decorator is also available to trace decorated method calls.

## 🧪 Tests

Tests are located in:

```text
backend/tests/
```

From the backend directory:

```bash
uv run pytest -v
```

Run a specific test file:

```bash
uv run pytest tests/tests_service/test_trajet_service.py -v
```

The pytest configuration in `pyproject.toml` adds `src/` to the Python import path.

When writing service tests, mock DAO and external API calls to control the results and avoid unintended database or network access.

Use pytest fixtures or `unittest.mock.patch` so that mocks are restored after each test.

### Test pattern

Service tests follow a **GIVEN / WHEN / THEN** structure and mock the DAO to isolate business logic:

```python
from unittest.mock import MagicMock


def test_creer_trajet_succes():
    # GIVEN
    ligne = Ligne(id_ligne=1)
    date_depart = datetime(2026, 6, 12, 8, 30)
    TrajetDao.creer_trajet = MagicMock(return_value=True)

    # WHEN
    service = TrajetService()
    resultat = service.creer_trajet(
        ligne=ligne,
        date_heure_depart=date_depart,
        duree_minutes=45,
        nb_places=50,
        tarif=15.0,
    )

    # THEN
    assert isinstance(resultat, Trajet)
    assert resultat.duree_minutes == 45
    TrajetDao.creer_trajet.assert_called_once()
```

## ⚙️ Configuration files

| File | Purpose |
| --- | --- |
| `pyproject.toml` | Project dependencies and pytest configuration |
| `uv.lock` | Dependency versions used by uv |
| `logging_config.yml` | Log handlers, formatting, and rotation |
| `src/main.py` | FastAPI application, router registration, and server entry point |

## 🔧 Adding or changing a feature

1. Define the request and response schemas in `src/schema/`.
2. Add or update the necessary business objects in `src/business_object/`.
3. Implement database operations in the DAO (`src/dao/`).
4. Implement business rules in the service (`src/service/`).
5. Expose the operation through a controller (`src/controller/`).
6. Add permission dependencies where required (`require_niveau`).
7. Add or update tests in `backend/tests/`.
8. Verify the endpoint in Swagger.

Validate simple input constraints in Pydantic schemas. Validate rules requiring database state in the service, such as checking that the total number of seats is sufficient for existing reservations.

### Getting started

When approaching the codebase for the first time, read the layers in this order:

1. `src/main.py` — see how routers are registered.
2. A controller (e.g. `trajet_controller.py`) — see how a request is validated, routed, and converted to a response.
3. The corresponding service (e.g. `trajet_service.py`) — see where business rules live.
4. The corresponding DAO (e.g. `trajet_dao.py`) — see how SQL is structured and transactions are managed.
5. The tests (`tests/tests_service/test_trajet_service.py`) — see how to verify changes without a running database.