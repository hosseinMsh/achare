# Advertisements & Job Requests

This module powers the core marketplace workflow: customers publish ads, contractors request them, and customers assign one contractor to finish the job.

## Key models

- `Advertisement` (`ads/models.py`)
  - `status`: `open` → `assigned` → `done` (or `canceled`)
  - `customer`, `contractor`, `contractor_done` flag/timestamp
- `JobRequest` (`ads/models.py`)
  - Unique per `(advertisement, contractor)`
  - `is_active` tracks cancellations.

## Permissions at a glance

- **Customer**: CRUD own ads, assign contractors, confirm done, cancel ads, view requests on own ads.
- **Contractor**: View open or assigned ads, create/cancel job requests, mark assigned ads done.
- **Support/Admin**: Full access, can delete ads.

## Endpoints

### Advertisements (router: `/api/ads/`)

- `GET /api/ads/` – List ads visible to the caller (role-aware).
- `POST /api/ads/` – Create (customers only).
- `GET /api/ads/<id>/` – Retrieve (object-level permission checks).
- `PATCH /api/ads/<id>/` – Update (owner + open status unless support/admin).
- `DELETE /api/ads/<id>/` – Support/admin only.

### Actions

- `POST /api/ads/assign/` – Customer assigns a contractor using `job_request_id`.
- `POST /api/ads/contractor-done/` – Assigned contractor marks work complete (`advertisement_id`).
- `POST /api/ads/confirm-done/` – Customer finalizes completion (`advertisement_id`), status → `done`.
- `POST /api/ads/cancel/` – Customer cancels (`advertisement_id`), unless already `done`.

### Job Requests (router: `/api/job-requests/`)

- `GET /api/job-requests/` – Contractor: own requests. Customer: requests on their ads. Support/admin: all.
- `POST /api/job-requests/` – Contractors request an **open** ad (`advertisement_id`).
- `PATCH /api/job-requests/<id>/` – Toggle `is_active` (owner or support/admin).
- `POST /api/job-requests/<id>/cancel/` – Convenience action to set `is_active=false`.
- `DELETE` – Not allowed.

## Status flows

1) Customer creates ad → `open`  
2) Contractors post job requests → customer reviews them  
3) Customer assigns a request → ad `assigned`, other requests deactivated  
4a) Contractor marks done → `contractor_done=true`  
4b) Customer confirms done → ad `done` (reviews now allowed)  
5) Customer can cancel any non-done ad → `canceled`

## Implementation references

- Models: `ads/models.py`
- Serializers: `ads/serializers.py`
- Views/permissions/actions: `ads/views.py`, `ads/permissions.py`
- Routes: `ads/urls.py`
