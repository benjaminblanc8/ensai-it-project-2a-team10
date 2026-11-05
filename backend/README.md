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

### Request processing

For a typical request:

1. FastAPI validates the input using a Pydantic schema.
2. The controller retrieves its dependencies and calls the service.
3. The service applies business rules and calls the DAO.
4. The DAO executes the SQL query and returns the result.
5. The controller returns data matching the response model.

Some operations also call the SNCF API through `ApiSncfService`.

### Business objects and schemas

Business objects represent entities manipulated by the application.

Pydantic schemas define the API contract. Creation and modification schemas contain user-editable fields. Response schemas also expose generated values, such as database identifiers and calculated journey durations.

When changing a schema, check the corresponding controller, service, and response conversion.

## 🗄️ Database access

Database connections are managed through `DBConnection` in:

```text
src/dao/db_connection.py
```

Connection settings are loaded from the environment.

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
utilisateur = Depends(
    require_niveau(NiveauHabilitation.COLLAB)
)
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

## ⚙️ Configuration files

| File | Purpose |
| --- | --- |
| `pyproject.toml` | Project dependencies and pytest configuration |
| `uv.lock` | Dependency versions used by uv |
| `logging_config.yml` | Log handlers, formatting, and rotation |
| `src/main.py` | FastAPI application, router registration, and server entry point |

## 🔧 Adding or changing a feature

1. Define the request and response schemas.
2. Add or update the necessary business objects.
3. Implement database operations in the DAO.
4. Implement business rules in the service.
5. Expose the operation through a controller.
6. Add permission dependencies where required.
7. Update relevant tests and verify the endpoint in Swagger.

Validate simple input constraints in Pydantic schemas. Validate rules requiring database state in the service, such as checking that the total number of seats is sufficient for existing reservations.