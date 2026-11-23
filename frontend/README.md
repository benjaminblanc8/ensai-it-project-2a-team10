# Frontend (Streamlit)

Web interface for the train booking API: search trips, book seats, and manage
stations, lines and trips depending on the user's role (CLIENT / COLLAB / ADMIN).

## Prerequisites

- Python 3.10+
- The backend API running (FastAPI) and reachable from this machine

## Setup

1. Install the dependencies:

   ```bash
   cd frontend
   pip install -r requirements.txt
   ```

Note : If you already installed the dependencies from the root of the project you don't need to run these command lines.

2. Create or edit the `.env` file in `frontend/` with the backend address:

   ```env
   BACKEND_URL=http://localhost:5000
   BACKEND_TIMEOUT=15
   ```

3. Start the backend, then launch the app **from the `frontend/` folder**
   (the log file path is relative to it):

   ```bash
   streamlit run src/app.py
   ```

The app opens at http://localhost:8501.

## Project structure

```
frontend/
├── .env                    # backend URL
├── logging_config.yml      # logging configuration
├── logs/                   # log files (frontend.log)
└── src/
    ├── app.py              # entry point (redirects to login or menu)
    ├── pages/              # one file per page
    └── utils/              # API client, auth guard, sidebar, station selector
```