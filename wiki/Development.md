# Development Guide

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Useful endpoints

- Swagger UI: `/api/docs/`
- OpenAPI JSON: `/api/schema/`
- Admin site: `/admin/` (create a superuser with `python manage.py createsuperuser`)

## Environment notes

- SQLite database by default (`achare/settings.py`). Override via `DATABASE_URL`-style settings if needed.
- CORS allows all origins and explicitly whitelists `http://localhost:5173`.
- JWT lifetimes: access 60 minutes, refresh 7 days.

## Testing

Run the full Django test suite:

```bash
python manage.py test
```

## Code map

- **Auth/Roles**: `accounts/` (custom `User`, `Role`, JWT serializer, role assignment).
- **Ads/Requests**: `ads/` (status flows, assignment actions, permissions).
- **Reviews**: `reviews/` (creation, contractor listings and profiles).
- **Tickets**: `tickets/` (user vs. support visibility, support responses).
- **Project config**: `achare/` (settings, URL routing, ASGI/WSGI).
