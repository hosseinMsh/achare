# Achare API

Achare is a Django REST Framework backend for a marketplace-style workflow where customers post jobs, contractors request and fulfill them, and support/admin users moderate the process. It also ships with JWT-based authentication, role management, reviews, and a lightweight support ticket system.

## Features

- **Authentication & roles**: Register/login with username, email, or phone; JWT tokens via SimpleJWT; dynamic roles (customer, contractor, support, admin).
- **Advertisements**: Customers create service requests, assign contractors from job requests, confirm completion, or cancel.
- **Job requests**: Contractors ask to work on open ads; customers pick one request to assign.
- **Reviews**: Customers review contractors once work is done; public contractor listings and profiles include stats.
- **Support tickets**: Authenticated users open tickets; support/admin users respond and close them.
- **API docs**: OpenAPI schema and Swagger UI at `/api/schema/` and `/api/docs/`.

## Project layout

- `achare/` – Django project settings, URLs, and ASGI/WSGI entry points.
- `accounts/` – Custom user model, JWT login with multi-identifier support, role management APIs.
- `ads/` – Advertisement and job-request models plus workflows for assignment and completion.
- `reviews/` – Contractor reviews, contractor listing/filtering, and profile endpoints.
- `tickets/` – Support ticket CRUD with role-aware visibility.
- `requirements.txt` – Python dependencies.

## Getting started

Prerequisites: Python 3.11+ and `pip`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate

# Optional: create an admin/superuser account
python manage.py createsuperuser

# Run the API
python manage.py runserver 0.0.0.0:8000
```

Open http://localhost:8000/api/docs/ for an interactive Swagger UI. Authenticate with a `Bearer <access_token>` header from the login endpoint.

## Authentication & roles

- **Register**: `POST /api/auth/register/` with `username`, `email`, `phone`, `password`, `first_name`, and `last_name`. New users receive the `customer` role by default.
- **Login**: `POST /api/auth/login/` with `identifier` (username/email/phone) and `password`; returns access and refresh JWT tokens plus basic user info.
- **Current user**: `GET /api/auth/me/` returns the authenticated user.
- **Set roles**: `POST /api/auth/users/<id>/roles/` (admin/support) with `roles: ["customer", "contractor", ...]`.

## API quick reference

All endpoints are prefixed with `/api/`.

### Advertisements & job requests

- `GET/POST /api/ads/` – List own ads (customer) or open/assigned ads (contractor); create ads (customer).
- `GET/PATCH/DELETE /api/ads/<id>/` – Retrieve/update ads with role-aware permissions; delete restricted to admin/support.
- `POST /api/ads/assign/` – Customer assigns a contractor from a job request (`job_request_id`).
- `POST /api/ads/contractor-done/` – Assigned contractor marks work complete (`advertisement_id`).
- `POST /api/ads/confirm-done/` – Customer confirms completion (`advertisement_id`), setting status to `done`.
- `POST /api/ads/cancel/` – Customer cancels a non-done ad (`advertisement_id`).
- `GET /api/job-requests/` – Contractors see their requests; customers see requests on their ads; support/admin see all.
- `POST /api/job-requests/` – Contractors request an open ad (`advertisement_id`).
- `POST /api/job-requests/<id>/cancel/` – Request owner cancels (sets `is_active` false).

### Reviews

- `POST /api/reviews/` – Customer creates a review for a `done` advertisement (`advertisement_id`, `rating`, `comment`).
- `GET /api/contractors/` – Public contractor list with `min_rating`, `min_reviews`, and `ordering` (`rating`, `-rating`, `review_count`, `-review_count`).
- `GET /api/contractors/<contractor_id>/profile/` – Contractor profile with stats and reviews.
- `GET /api/contractors/<contractor_id>/reviews/` – Contractor reviews; filter with `?rating=`.

### Support tickets

- `GET/POST /api/tickets/` – Authenticated users create and view their tickets; support/admin see all.
- `GET/PATCH /api/tickets/<id>/` – Users update their own tickets; support/admin can add `response` and change `status` (`open`, `pending`, `closed`).
- `DELETE /api/tickets/<id>/` – Only support/admin.

## Roles & permissions at a glance

- **Customer**: Create ads; view/manage own ads; assign contractors; confirm/cancel work; create reviews; view related job requests and tickets.
- **Contractor**: View open or assigned ads; create/cancel job requests; mark assigned ads as done; appear in contractor listings.
- **Support/Admin**: View all ads, requests, reviews, and tickets; set user roles; delete ads/tickets. Superusers implicitly bypass role checks.

## Running tests

```bash
python manage.py test
```

## API documentation & schema

- **Swagger UI**: `/api/docs/`
- **OpenAPI JSON**: `/api/schema/`

Use these during development to explore payloads, parameters, and authentication requirements.
