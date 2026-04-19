# ABUAB Inventory

FastAPI-based inventory and POS web application with local SQLite storage and optional PyWebView desktop shell.

## Security Notes

- Authentication secret is loaded from environment variable `ABUAB_SECRET_KEY`.
- Registration is locked down:
  - First account bootstrap must be an admin.
  - After bootstrap, only authenticated admins can create users.
- Privileged routes enforce role checks server-side.

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Create your runtime config:
   - Copy `.env.example` to `.env` and set a strong `ABUAB_SECRET_KEY`.
4. Start the app:
   - `uvicorn app.main:app --reload`
5. Open:
   - `http://127.0.0.1:8000/login`

## Desktop Mode

To run desktop shell mode:

- `python app/main.py`

## GitHub Publish Checklist

- Confirm `.env` is not committed.
- Confirm `venv/`, `build/`, `dist/`, and local database files are not committed.
- Rotate any old secrets that were previously hardcoded.
- Create initial admin account after startup.
