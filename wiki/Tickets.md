# Support Tickets

Authenticated users can open support tickets. Support/admin users can respond and close them.

## Key model

- `Ticket` (`tickets/models.py`)
  - `user`, `title`, `message`
  - `response` (support reply), `status` (`open`, `pending`, `closed`)
  - Timestamps

## Endpoints (router: `/api/tickets/`)

- `GET /api/tickets/` – Users see their own tickets; support/admin see all.
- `POST /api/tickets/` – Create ticket (`title`, `message`).
- `GET /api/tickets/<id>/` – Retrieve; visibility follows the same rules.
- `PATCH /api/tickets/<id>/` – Users can update their ticket fields; support/admin can also set `response` and `status`.
- `DELETE /api/tickets/<id>/` – Support/admin only.

## Implementation references

- Models: `tickets/models.py`
- Serializers: `tickets/serializers.py`
- Views: `tickets/views.py`
- Routes: `tickets/urls.py`
