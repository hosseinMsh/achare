# Authentication & Roles

## Overview

Authentication uses JSON Web Tokens (JWT) via `djangorestframework-simplejwt`. Users can log in with **username, email, or phone**. Roles are dynamic (`Role` model) and attached to users to drive permissions across the API.

## Endpoints

- **Register** – `POST /api/auth/register/`  
  Body: `username`, `email`, `phone`, `password`, `first_name`, `last_name`  
  Default role: `customer`.

- **Login** – `POST /api/auth/login/`  
  Body: `identifier` (username/email/phone), `password`  
  Returns `access` and `refresh` tokens plus user info.

- **Current user** – `GET /api/auth/me/`  
  Requires `Authorization: Bearer <access>`.

- **Set roles (admin/support)** – `POST /api/auth/users/<user_id>/roles/`  
  Body: `roles: ["customer", "contractor", ...]`.

## Roles in practice

- **Customer** – Own ads, assign contractors, confirm/cancel work, create reviews, see ticket history.
- **Contractor** – Browse open or assigned ads, create/cancel job requests, mark work done, appear in contractor listings.
- **Support/Admin** – Full visibility, manage roles, delete ads/tickets, respond to tickets. Superusers bypass checks.

## Tokens

- Access token lifetime: 60 minutes.  
- Refresh token lifetime: 7 days.  
- Include `Authorization: Bearer <access_token>` on protected endpoints.

## Model/Serializer references

- `accounts/models.py` – `User`, `Role`.
- `accounts/jwt.py` – `IdentifierTokenObtainPairSerializer` enabling multi-identifier login.
- `accounts/serializers.py` – Registration and role assignment.
- `accounts/views.py` – Register/Login/Me/SetUserRoles views.
