# Reviews

Customers can leave a single review for a contractor after an advertisement is completed.

## Key model

- `Review` (`reviews/models.py`)
  - One-to-one with `Advertisement`
  - `contractor`, `author` (customer), `rating` (1–5), `comment`, timestamps

## Endpoints

- `POST /api/reviews/` – Create review  
  Body: `advertisement_id`, `rating` (1–5), `comment`  
  Rules: Ad must be `done`, have a contractor, belong to the caller, and not already reviewed.

- `GET /api/contractors/` – Public contractor list with optional filters:  
  - `min_rating` (float)  
  - `min_reviews` (int)  
  - `ordering`: `rating`, `-rating`, `review_count`, `-review_count`  
  Response includes contractor basics, `done_ads`, `avg_rating`, `review_count`.

- `GET /api/contractors/<id>/profile/` – Contractor stats plus all reviews.
- `GET /api/contractors/<id>/reviews/` – Reviews for a contractor; filter with `?rating=1..5`.

## Workflow

1) Contractor completes work; customer confirms (`/api/ads/confirm-done/` sets ad to `done`).  
2) Customer submits a review referencing the advertisement.  
3) Reviews contribute to contractor averages and listing filters.

## Implementation references

- Models: `reviews/models.py`
- Serializers: `reviews/serializers.py`
- Views: `reviews/views.py`
- Routes: `reviews/urls.py`
