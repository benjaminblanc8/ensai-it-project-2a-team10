# Trajecto

## Overview

**Trajecto** is a web application for managing railway journeys. It provides a REST API (built with FastAPI) that allows users to:

- **Search and manage train stations** and **lines**
- **Create, modify, and delete journeys** with departure time, duration, pricing, and seat availability
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

Use **`POST /connexion/`** with **form data** (not JSON):

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