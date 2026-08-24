# Society Maintenance Tracker — API Documentation

## 1. API Overview

The Society Maintenance Tracker exposes a RESTful API through the FastAPI backend.

### Base URL

```text
/api/v1
```

### Content Type

Most requests and responses use:

```text
application/json
```

Complaint creation with an optional image uses:

```text
multipart/form-data
```

### Authentication

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

The API uses JWT-based authentication.

---

# 2. Authentication

## POST `/auth/register`

Creates a new resident account.

### Access

Public

### Request

```json
{
  "name": "Ritesh Raushan",
  "email": "ritesh@example.com",
  "password": "secure-password"
}
```

### Response — `201 Created`

```json
{
  "id": "uuid",
  "name": "Ritesh Raushan",
  "email": "ritesh@example.com",
  "role": "RESIDENT",
  "is_active": true
}
```

Public registration cannot create an admin account.

---

## POST `/auth/login`

Authenticates an active user.

### Access

Public

### Request

```json
{
  "email": "ritesh@example.com",
  "password": "secure-password"
}
```

### Response — `200 OK`

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

Inactive users receive an authentication error and cannot log in.

---

## GET `/auth/me`

Returns information about the currently authenticated user.

### Access

Authenticated users

### Response — `200 OK`

```json
{
  "id": "uuid",
  "name": "Ritesh Raushan",
  "email": "ritesh@example.com",
  "role": "RESIDENT",
  "is_active": true
}
```

---

# 3. User Management

## GET `/admin/users`

Returns resident accounts.

### Access

Admin only

### Query Parameters

```text
page
page_size
search
is_active
sort_by
sort_order
```

### Response

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 50,
  "total_pages": 3
}
```

---

## PATCH `/admin/users/{user_id}/status`

Activates or deactivates a resident account.

### Access

Admin only

### Request

```json
{
  "is_active": false
}
```

### Response — `200 OK`

```json
{
  "id": "uuid",
  "is_active": false
}
```

An inactive user cannot log in or receive email notifications.

---

# 4. Complaint Categories

## GET `/categories`

Returns active complaint categories available to residents.

### Access

Authenticated users

### Response

```json
[
  {
    "id": "uuid",
    "name": "Plumbing",
    "description": "Water supply and plumbing issues"
  },
  {
    "id": "uuid",
    "name": "Electrical",
    "description": "Electrical maintenance issues"
  }
]
```

---

## GET `/admin/categories`

Returns all complaint categories, including inactive categories.

### Access

Admin only

---

## POST `/admin/categories`

Creates a new complaint category.

### Access

Admin only

### Request

```json
{
  "name": "Parking",
  "description": "Parking-related complaints"
}
```

### Response — `201 Created`

```json
{
  "id": "uuid",
  "name": "Parking",
  "description": "Parking-related complaints",
  "is_active": true
}
```

---

## PATCH `/admin/categories/{category_id}`

Updates a complaint category.

### Access

Admin only

### Request

```json
{
  "name": "Parking",
  "description": "Parking and vehicle-related issues"
}
```

---

## PATCH `/admin/categories/{category_id}/status`

Activates or deactivates a category.

### Access

Admin only

### Request

```json
{
  "is_active": false
}
```

Deactivating a category does not modify existing complaints using that category.

---

# 5. Resident Complaint APIs

## POST `/complaints`

Creates a new complaint.

### Access

Active resident only

### Content Type

```text
multipart/form-data
```

### Fields

```text
category_id
description
photo (optional)
```

### Example

```text
category_id = <category UUID>
description = Water leakage near Block B
photo = leakage.jpg
```

### Response — `201 Created`

```json
{
  "id": "uuid",
  "category": {
    "id": "uuid",
    "name": "Plumbing"
  },
  "description": "Water leakage near Block B",
  "photo_url": "https://...",
  "status": "OPEN",
  "priority": "MEDIUM",
  "created_at": "2026-08-24T10:30:00Z"
}
```

---

## GET `/complaints`

Returns complaints belonging to the authenticated resident.

### Access

Active resident only

### Query Parameters

```text
page
page_size
status
category_id
priority
sort_by
sort_order
```

### Response

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 12,
  "total_pages": 1
}
```

Residents can only retrieve their own complaints.

---

## GET `/complaints/{complaint_id}`

Returns detailed information about a complaint.

### Access

* Complaint owner
* Admin

### Response

```json
{
  "id": "uuid",
  "category": {
    "id": "uuid",
    "name": "Plumbing"
  },
  "description": "Water leakage near Block B",
  "photo_url": "https://...",
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "created_at": "2026-08-24T10:30:00Z",
  "updated_at": "2026-08-24T15:00:00Z",
  "resolved_at": null,
  "is_overdue": false
}
```

---

## GET `/complaints/{complaint_id}/history`

Returns the complete status history for a complaint.

### Access

* Complaint owner
* Admin

### Response

```json
[
  {
    "id": "uuid",
    "old_status": "OPEN",
    "new_status": "IN_PROGRESS",
    "actor": {
      "id": "uuid",
      "name": "Admin"
    },
    "note": "Maintenance team assigned",
    "created_at": "2026-08-24T12:00:00Z"
  }
]
```

History records are read-only through the API.

---

# 6. Admin Complaint APIs

## GET `/admin/complaints`

Returns all complaints.

### Access

Admin only

### Query Parameters

```text
page
page_size

status
category_id
priority

date_from
date_to

is_overdue

sort_by
sort_order
```

### Example

```text
GET /api/v1/admin/complaints?status=OPEN&priority=HIGH&is_overdue=true
```

### Response

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 25,
  "total_pages": 2
}
```

Overdue complaints can be filtered and should be prioritized in the admin interface.

---

## PATCH `/admin/complaints/{complaint_id}/status`

Updates the status of a complaint.

### Access

Admin only

### Request

```json
{
  "status": "IN_PROGRESS",
  "note": "Maintenance team assigned."
}
```

### Valid Transitions

```text
OPEN → IN_PROGRESS
OPEN → RESOLVED
IN_PROGRESS → RESOLVED
```

### Response — `200 OK`

```json
{
  "id": "uuid",
  "status": "IN_PROGRESS",
  "updated_at": "2026-08-24T15:00:00Z"
}
```

The operation must:

1. Validate the status transition.
2. Update the complaint.
3. Create a history record.
4. Commit both changes atomically.
5. Trigger notification processing.

---

## PATCH `/admin/complaints/{complaint_id}/priority`

Updates complaint priority.

### Access

Admin only

### Request

```json
{
  "priority": "HIGH"
}
```

### Valid Values

```text
LOW
MEDIUM
HIGH
```

### Response — `200 OK`

```json
{
  "id": "uuid",
  "priority": "HIGH"
}
```

---

# 7. Notice APIs

## GET `/notices`

Returns notices visible to residents.

### Access

Authenticated users

### Query Parameters

```text
page
page_size
```

### Ordering

Notices are ordered by:

```text
is_important DESC
created_at DESC
```

### Response

```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Water Supply Maintenance",
      "content": "Water supply will be unavailable from 2 PM to 5 PM.",
      "is_important": true,
      "created_at": "2026-08-24T09:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1,
  "total_pages": 1
}
```

---

## POST `/admin/notices`

Creates a new notice.

### Access

Admin only

### Request

```json
{
  "title": "Water Supply Maintenance",
  "content": "Water supply will be unavailable from 2 PM to 5 PM.",
  "is_important": true
}
```

### Response — `201 Created`

```json
{
  "id": "uuid",
  "title": "Water Supply Maintenance",
  "content": "Water supply will be unavailable from 2 PM to 5 PM.",
  "is_important": true,
  "created_at": "2026-08-24T09:00:00Z"
}
```

If `is_important` is `true`, notification processing is triggered for active residents.

---

## PATCH `/admin/notices/{notice_id}`

Updates a notice.

### Access

Admin only

### Request

```json
{
  "title": "Updated Notice",
  "content": "Updated announcement.",
  "is_important": false
}
```

---

## DELETE `/admin/notices/{notice_id}`

Deletes a notice.

### Access

Admin only

### Response

```text
204 No Content
```

---

# 8. Dashboard APIs

## GET `/admin/dashboard`

Returns aggregated complaint statistics.

### Access

Admin only

### Response

```json
{
  "total_complaints": 128,
  "open": 35,
  "in_progress": 22,
  "resolved": 71,
  "overdue": 12,
  "by_category": {
    "Plumbing": 42,
    "Electrical": 28,
    "Cleaning": 23
  },
  "by_priority": {
    "LOW": 40,
    "MEDIUM": 65,
    "HIGH": 23
  }
}
```

Dashboard statistics are calculated by the backend.

---

# 9. System Settings APIs

## GET `/admin/settings`

Returns configurable application settings.

### Access

Admin only

### Response

```json
{
  "overdue_threshold_days": 3
}
```

---

## PATCH `/admin/settings/overdue-threshold`

Updates the overdue threshold.

### Access

Admin only

### Request

```json
{
  "days": 3
}
```

The value must be a positive integer.

---

# 10. HTTP Status Codes

The API uses standard HTTP status codes.

| Status | Meaning                                    |
| ------ | ------------------------------------------ |
| `200`  | Request successful                         |
| `201`  | Resource successfully created              |
| `204`  | Request successful with no response body   |
| `400`  | Invalid request                            |
| `401`  | Authentication required or invalid         |
| `403`  | Authenticated but insufficient permissions |
| `404`  | Resource not found                         |
| `409`  | Resource conflict                          |
| `422`  | Request validation failed                  |
| `500`  | Internal server error                      |

---

# 11. Error Response Format

API errors should use a consistent structure.

Example:

```json
{
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "A resolved complaint cannot be reopened."
  }
}
```

Validation errors may contain field-level details:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": {
      "description": "Description is required."
    }
  }
}
```

---

# 12. Authorization Matrix

| Endpoint                                  | Resident | Admin |
| ----------------------------------------- | -------: | ----: |
| `POST /auth/register`                     |        ✓ |     ✓ |
| `POST /auth/login`                        |        ✓ |     ✓ |
| `GET /auth/me`                            |        ✓ |     ✓ |
| `GET /categories`                         |        ✓ |     ✓ |
| `POST /complaints`                        |        ✓ |     — |
| `GET /complaints`                         |        ✓ |     — |
| `GET /complaints/{id}`                    |      Own |     ✓ |
| `GET /complaints/{id}/history`            |      Own |     ✓ |
| `GET /admin/complaints`                   |        — |     ✓ |
| `PATCH /admin/complaints/{id}/status`     |        — |     ✓ |
| `PATCH /admin/complaints/{id}/priority`   |        — |     ✓ |
| `GET /notices`                            |        ✓ |     ✓ |
| `POST /admin/notices`                     |        — |     ✓ |
| `PATCH /admin/notices/{id}`               |        — |     ✓ |
| `DELETE /admin/notices/{id}`              |        — |     ✓ |
| `GET /admin/dashboard`                    |        — |     ✓ |
| `GET /admin/users`                        |        — |     ✓ |
| `PATCH /admin/users/{id}/status`          |        — |     ✓ |
| `POST /admin/categories`                  |        — |     ✓ |
| `PATCH /admin/categories/{id}`            |        — |     ✓ |
| `PATCH /admin/categories/{id}/status`     |        — |     ✓ |
| `GET /admin/settings`                     |        — |     ✓ |
| `PATCH /admin/settings/overdue-threshold` |        — |     ✓ |

---

# 13. API Design Principles

The API follows these principles:

1. **Versioned API** — All application endpoints are under `/api/v1`.
2. **RESTful resources** — Endpoints are organized around application resources.
3. **Backend authorization** — Permissions are enforced on the server.
4. **Consistent responses** — Similar operations use consistent response structures.
5. **Pagination** — Collection endpoints support pagination.
6. **Filtering and sorting** — Administrative complaint endpoints support flexible querying.
7. **Validation** — Request data is validated before business logic executes.
8. **Standard HTTP semantics** — HTTP status codes communicate operation results.
9. **Secure authentication** — Protected endpoints require a valid JWT.
10. **Separation of concerns** — API endpoints delegate business logic to service-layer components.