# MTA Hotel HMS

Production-ready MVP foundation for a modular Django monolith Hotel Management System with a React + Vite frontend.

This repository intentionally contains only the foundation: project structure, environment-based settings, REST/JWT wiring, Docker-ready configuration, and placeholder business modules. Hotel workflows will be implemented later.

## Run Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements/development.txt
copy ..\.env.example .env
py manage.py migrate
py manage.py runserver
```

Backend health check:

```text
http://localhost:8000/api/v1/health/
```

## Run Frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend dev server:

```text
http://localhost:5173
```

## Docker

```powershell
copy .env.example .env
docker compose up --build
```

## Configuration

Copy `.env.example` to `.env` and provide real values for secrets and database credentials. Production must set `DJANGO_DEBUG=False`, a strong `DJANGO_SECRET_KEY`, trusted hosts/origins, and PostgreSQL credentials.

## Database Schema

The Django migration source lives in `backend/apps/*/migrations/`.

A readable PostgreSQL schema reference is available at `docs/database_schema.sql`.
