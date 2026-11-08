# Trajecto

## Overview

**Trajecto** is a web application for managing railway journeys. It provides a REST API (built with FastAPI) that allows users to:

- **Search and manage train stations** and **lines**
- **Create, modify, and delete journeys** with departure time, duration, pricing, and seat availability
- **Reserve seats** on a journey and **cancel** reservations
- **Manage user accounts** with a tiered permission system:
  - `CLIENT` (level 1) – basic access
  - `COLLAB` (level 2) – extended access
  - `ADMIN` (level 3) – full access, including role management

The application integrates with the **SNCF API** to fetch real-time station and line data.

---

## Installation & Quick Start

### Prerequisites

- Python 3.11+
- A running PostgreSQL database
- Access to the SNCF API

### Step 1: Install dependencies

From the repository root:

```bash
pip install -r requirements.txt
```

Alternatively, you can install from `backend/pyproject.toml`:

```bash
cd backend
pip install -e \".[dev]\"
```

### Step 2: Configure the environment

Create a `.env` file in the **repository root** with the following content:

```env
POSTGRES_HOST=postgresql-cnpg-738928-rw.user-benjaminblanc
POSTGRES_PORT=5432
POSTGRES_DATABASE=defaultdb
POSTGRES_USER=user-benjaminblanc
POSTGRES_PASSWORD=***
POSTGRES_SCHEMA=public
UVICORN_HOST=0.0.0.0
UVICORN_PORT=5000
BACKEND_URL=http://localhost:5000/
BACKEND_TIMEOUT=5
JWT_SECRET_KEY=***
```

> 🔑 Replace `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` with actual values. Ask the team if you don't have them.
> 🔑 You might need the `SNCF_API_KEY` value if you update the database with Navitia data. Ask the team in that case.

### Step 3: Start the server

```bash
cd backend
python src/main.py
```

The server starts on `http://127.0.0.1:5000`.

### Step 4: Access the interactive documentation (Swagger)

Once the server is running, open your browser to:

```
http://127.0.0.1:5000/docs
```

> The root URL (`http://127.0.0.1:5000/`) automatically redirects to `/docs`.

**On Onyxia (remote environment):**

1. In the VS Code service, open the **Ports** panel (right sidebar).
2. Find the entry for **port 5000**.
3. Click the associated link to open Swagger in your browser.

The URL will look like:

```
https://<your-onyxia-service>.xxx.onyxia.org/proxy/5000/docs
```

### Quick test

In another terminal, verify the server is responding:

```bash
curl http://localhost:5000/hello/World
```

Expected response:

```json
{"message": "Hello World"}
```

---

## Using the API

### Endpoint Summary

#### No authentication required

| Method | Endpoint | Use Case |
|--------|----------|----------|
| `POST` | `/utilisateur/` | Create a user account |
| `POST` | `/connexion/` | Log in, obtain JWT token |

#### `CLIENT` (level 1)

| Method | Endpoint | Use Case |
|--------|----------|----------|
| `GET` | `/gare/id/{id_gare}` | Search station by ID |
| `GET` | `/gare/nom_gare/{nom_gare}` | Search stations by name (SNCF) |
| `GET` | `/ligne/{id_ligne}` | Search line by ID |
| `GET` | `/trajet/` | Search journeys between two stations |
| `GET` | `/trajet/{id_trajet}` | Search journey by ID |
| `POST` | `/reservation/` | Reserve a seat on a journey |
| `GET` | `/reservation/mes-reservations` | List my reservations |
| `DELETE` | `/reservation/{id_reservation}` | Cancel a reservation |

#### `COLLAB` (level 2) — includes all `CLIENT` endpoints

| Method | Endpoint | Use Case |
|--------|----------|----------|
| `POST` | `/gare/` | Add a station |
| `DELETE` | `/gare/{id_gare}` | Delete a station |
| `POST` | `/ligne/` | Create a line between two stations |
| `DELETE` | `/ligne/{id_ligne}` | Delete a line |
| `POST` | `/trajet/` | Create a journey (duration from SNCF) |
| `PUT` | `/trajet/{id_trajet}` | Modify a journey |
| `DELETE` | `/trajet/{id_trajet}` | Delete a journey |

#### `ADMIN` (level 3) — includes all `CLIENT` + `COLLAB` endpoints

| Method | Endpoint | Use Case |
|--------|----------|----------|
| `PUT` | `/utilisateur/role` | Change a user's permission level |"

### Permission Levels

| Level | Name | Capabilities |
|-------|------|--------------|
| 1 | `CLIENT` | Read access to stations, lines, journeys + manage own reservations |
| 2 | `COLLAB` | All `CLIENT` operations, **plus** write access (create/modify/delete stations, lines, journeys) |
| 3 | `ADMIN` | All `CLIENT` + `COLLAB` operations, **plus** role management (`PUT /utilisateur/role`) |

> ⚠️ All endpoints require at least `CLIENT` (level 1). Write operations (`POST`, `PUT`, `DELETE`) on gares, lignes, and trajets require at least `COLLAB` (level 2).

### Creating an Account

To create a new user account, use the **`POST /utilisateur/`** endpoint.

**Request body:**

| Field    | Type   | Description |
|----------|--------|-------------|
| `pseudo` | string | Username    |
| `mdp`    | string | Password    |

**Example:**

```bash
curl -X POST http://localhost:5000/utilisateur/ \
  -H "Content-Type: application/json" \
  -d '{"pseudo": "john_doe", "mdp": "securepassword123"}'
```

A newly created account is assigned the default `CLIENT` (level 1) permission.

### Logging In (Obtaining a Token)

> 💡 **In Swagger:** the easiest way is to click the **"Authorize"** button (top-right corner). Enter your `username` and `password`, and the token is automatically attached to all subsequent requests.

Alternatively, use **`POST /connexion/`** with **form data** (not JSON):

| Field      | Type   | Description |
|------------|--------|-------------|
| `username` | string | Username    |
| `password` | string | Password    |

**Example:**

```bash
curl -X POST http://localhost:5000/connexion/ \
  -d "username=john_doe&password=securepassword123"
```

**Successful response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "utilisateur": {
    "id": 1,
    "pseudo": "john_doe",
    "habilitation": "CLIENT"
  }
}
```

> ⏳ Tokens expire after **7 days**.

### Using the Token (Authenticated Requests)

Protected endpoints require a **Bearer token** in the `Authorization` header:

```bash
curl http://localhost:5000/<protected-endpoint> \
  -H "Authorization: Bearer <your_access_token>"
```

If the token is missing, invalid, or expired, a `401` error is returned.

### Managing Stations (Gares)

#### Add a Station

**`POST /gare/`**

| Field | Type   | Description  |
|-------|--------|--------------|
| `nom` | string | Station name |
| `ville`| string | City         |

```bash
curl -X POST http://localhost:5000/gare/ \
  -H "Content-Type: application/json" \
  -d '{"nom": "Paris Gare de Lyon", "ville": "Paris"}'
```

#### Search Stations by Name (SNCF API)

**`GET /gare/nom_gare/{nom_gare}`** — searches the **SNCF API** (not the local DB).

```bash
curl http://localhost:5000/gare/nom_gare/Paris
```

Returns a list of matching stations.

#### Search a Station by ID

**`GET /gare/id/{id_gare}`**

```bash
curl http://localhost:5000/gare/id/42
```

#### Delete a Station

**`DELETE /gare/{id_gare}`**

```bash
curl -X DELETE http://localhost:5000/gare/42
```

---

### Managing Lines (Lignes)

#### Create a Line

**`POST /ligne/`** — creates a line between two existing stations.

| Field            | Type | Description        |
|------------------|------|--------------------|
| `id_gare_depart` | int  | ID of departure station |
| `id_gare_arrivee`| int  | ID of arrival station   |

```bash
curl -X POST http://localhost:5000/ligne/ \
  -H "Content-Type: application/json" \
  -d '{"id_gare_depart": 1, "id_gare_arrivee": 5}'
```

**Response (`LigneReadModel`):**

```json
{
  "id_ligne": 10,
  "gare_depart": { "id_gare": 1, "nom": "Paris Gare de Lyon", "ville": "Paris" },
  "gare_arrivee": { "id_gare": 5, "nom": "Lyon Part-Dieu", "ville": "Lyon" },
  "date_creation": "2025-01-15"
}
```

#### Search a Line by ID

**`GET /ligne/{id_ligne}`**

```bash
curl http://localhost:5000/ligne/10
```

#### Delete a Line

**`DELETE /ligne/{id_ligne}`**

```bash
curl -X DELETE http://localhost:5000/ligne/10
```

---

### Managing Journeys (Trajets)

#### Create a Journey

**`POST /trajet/`** — creates a journey on an existing line. The **duration is automatically estimated** via the SNCF API based on the departure time.

| Field              | Type     | Description                              |
|--------------------|----------|------------------------------------------|
| `nom_gare_depart`  | string   | Name of the departure station            |
| `nom_gare_arrivee` | string   | Name of the arrival station              |
| `date_heure_depart`| datetime | Departure date and time (ISO 8601)       |
| `nb_places`        | int      | Total number of seats                    |
| `tarif`            | float    | Price per seat (€)                       |

```bash
curl -X POST http://localhost:5000/trajet/ \
  -H "Content-Type: application/json" \
  -d '{
    "nom_gare_depart": "Paris Gare de Lyon",
    "nom_gare_arrivee": "Lyon Part-Dieu",
    "date_heure_depart": "2025-07-20T09:00:00",
    "nb_places": 20,
    "tarif": 39.50
  }'
```

> ⚡ The server calls the SNCF API to compute the duration. If no route is found, a `422` is returned.

**Response (`TrajetReadModel`):**

```json
{
  "id_trajet": 100,
  "id_ligne": 10,
  "date_heure_depart": "2025-07-20T09:00:00",
  "duree_minutes": 155,
  "nb_places": 20,
  "tarif": 39.50,
  "places_reservees": 0,
  "places_disponibles": 20
}
```

#### Search Journeys Between Two Stations

**`GET /trajet/`** — returns all journeys on the line connecting the two given stations.

| Query param         | Type   | Description           |
|---------------------|--------|-----------------------|
| `nom_gare_depart`   | string | Departure station name|
| `nom_gare_arrivee`  | string | Arrival station name  |

```bash
curl "http://localhost:5000/trajet/?nom_gare_depart=Paris%20Gare%20de%20Lyon&nom_gare_arrivee=Lyon%20Part-Dieu"
```

Returns an empty array `[]` if no line exists between the two stations.

#### Search a Journey by ID

**`GET /trajet/{id_trajet}`**

```bash
curl http://localhost:5000/trajet/100
```

#### Modify a Journey

**`PUT /trajet/{id_trajet}`**

| Field              | Type     | Description           |
|--------------------|----------|-----------------------|
| `id_ligne`         | int      | Line ID               |
| `date_heure_depart`| datetime | New departure datetime|
| `duree_minutes`    | int      | New duration (minutes)|
| `nb_places`        | int      | Total seats           |
| `tarif`            | float    | New price (€)         |

```bash
curl -X PUT http://localhost:5000/trajet/100 \
  -H "Content-Type: application/json" \
  -d '{
    "id_ligne": 10,
    "date_heure_depart": "2025-07-20T10:30:00",
    "duree_minutes": 155,
    "nb_places": 25,
    "tarif": 42.00
  }'
```

> ⚠️ Modifying a journey does **not** re-calculate the duration from SNCF. You must pass the correct `duree_minutes` yourself.

#### Delete a Journey

**`DELETE /trajet/{id_trajet}`**

```bash
curl -X DELETE http://localhost:5000/trajet/100
```

**Response:**

```json
{"message": "Trajet supprimé avec succès"}
```

---

### Managing Reservations

Any `CLIENT` user can reserve a seat on a journey, view their reservations, and cancel them. The system automatically tracks seat availability.

#### Reserve a Seat

**`POST /reservation/`** — reserves one seat on a journey for the connected user.

> ⚠️ The journey must exist and have at least one available seat (`places_disponibles > 0`). If the journey is full, a `409` error is returned.

| Field      | Type | Description         |
|------------|------|---------------------|
| `id_trajet`| int  | ID of the journey to book |

```bash
curl -X POST http://localhost:5000/reservation/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <client_access_token>" \
  -d '{"id_trajet": 100}'
```

**Successful response:**

```json
{
  "message": "Réservation effectuée avec succès.",
  "id_reservation": 5
}
```

**Error responses:**

| Status | Cause |
|--------|-------|
| `401`  | Missing or invalid token |
| `404`  | Journey not found |
| `409`  | No seats available on this journey |

#### List My Reservations

**`GET /reservation/mes-reservations`** — returns all reservations made by the connected user, with journey details.

```bash
curl http://localhost:5000/reservation/mes-reservations \
  -H "Authorization: Bearer <client_access_token>"
```

**Successful response:**

```json
[
  {
    "id_reservation": 5,
    "utilisateur": {
      "id_utilisateur": 1,
      "pseudo": "john_doe",
      "niveau": "CLIENT"
    },
    "trajet": {
      "id_trajet": 100,
      "date_heure_depart": "2025-07-20T09:00:00",
      "duree_minutes": 155,
      "nb_places": 20,
      "tarif": 39.50,
      "places_reservees": 3
    }
  }
]
```

#### Cancel a Reservation

**`DELETE /reservation/{id_reservation}`** — cancels a reservation belonging to the connected user and frees the seat.

```bash
curl -X DELETE http://localhost:5000/reservation/5 \
  -H "Authorization: Bearer <client_access_token>"
```

**Successful response:**

```json
{
  "message": "Réservation annulée avec succès.",
  "id_reservation": 5
}
```

**Error responses:**

| Status | Cause |
|--------|-------|
| `401`  | Missing or invalid token |
| `403`  | The reservation belongs to another user |
| `404`  | Reservation not found |

> 💡 When a seat is reserved, `places_reservees` on the journey increases by 1. When a reservation is cancelled, it decreases by 1. The `places_disponibles` field (visible on all journey responses) always reflects `nb_places - places_reservees`.

---

### Changing a User's Permission Level (Admin Only)

An **admin** user can change another user's permission level using **`PUT /utilisateur/role`**.

The admin's identity is extracted from the Bearer token — no need to pass it in the body.

**Request body (JSON):**

| Field                   | Type | Description                                    |
|-------------------------|------|------------------------------------------------|
| `id_utilisateur`        | int  | ID of the target user whose level will be changed |
| `nouvelle_habilitation` | int  | New level: `1` (CLIENT), `2` (COLLAB), `3` (ADMIN) |

**Example:**

```bash
curl -X PUT http://localhost:5000/utilisateur/role \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_access_token>" \
  -d '{"id_utilisateur": 5, "nouvelle_habilitation": 3}'
```

> 🔒 This endpoint is restricted: only a user with `ADMIN` level can perform a role change. Otherwise a `403` error is returned.

---

## Running Tests

```bash
cd backend
pytest
```