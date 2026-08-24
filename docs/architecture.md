# Society Maintenance Tracker — System Architecture

## 1. Architecture Overview

The Society Maintenance Tracker follows a client-server architecture using a React frontend, FastAPI backend, PostgreSQL database, external image storage, and an external email delivery service.

The backend follows a **modular monolithic architecture**. Application functionality is separated into modules while being deployed as a single backend service.

This approach keeps the system simple to deploy and maintain while allowing individual modules to evolve independently.

---

## 2. Technology Stack

| Layer               | Technology                  |
| ------------------- | --------------------------- |
| Frontend            | React                       |
| Styling             | Tailwind CSS                |
| Backend             | FastAPI                     |
| API                 | REST                        |
| ORM                 | SQLAlchemy                  |
| Database            | PostgreSQL                  |
| Authentication      | JWT                         |
| Image Storage       | Cloudinary / Object Storage |
| Email               | Resend                      |
| Frontend Deployment | Vercel                      |
| Backend Deployment  | Render / Railway            |
| Database Hosting    | Managed PostgreSQL          |

---

## 3. High-Level Architecture

```text
                         ┌─────────────────────┐
                         │       Users         │
                         │  Resident / Admin   │
                         └──────────┬──────────┘
                                    │
                                    │ HTTPS
                                    ▼
                         ┌─────────────────────┐
                         │   React Frontend    │
                         │   React + Tailwind  │
                         └──────────┬──────────┘
                                    │
                                    │ REST API
                                    ▼
                    ┌──────────────────────────────┐
                    │        FastAPI Backend       │
                    │                              │
                    │  Authentication & RBAC       │
                    │  Complaint Management        │
                    │  Category Management         │
                    │  User Management             │
                    │  Notice Management            │
                    │  Dashboard                    │
                    │  Notification Service         │
                    │  Upload Service               │
                    └──────────────┬───────────────┘
                                   │
                  ┌────────────────┼─────────────────┐
                  │                │                 │
                  ▼                ▼                 ▼
          ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
          │ PostgreSQL   │ │    Image     │ │    Email     │
          │   Database   │ │   Storage    │ │   Service    │
          │              │ │  Cloudinary  │ │    Resend    │
          └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 4. Frontend Architecture

The frontend is implemented using React and Tailwind CSS.

The frontend is responsible for:

* User registration and login.
* Authentication state management.
* Role-based navigation.
* Resident dashboard.
* Complaint creation.
* Complaint listing.
* Complaint details and history.
* Notice board.
* Admin dashboard.
* Complaint management.
* Category management.
* User management.
* API communication.

The frontend communicates with the backend exclusively through REST APIs.

Frontend authorization is used for user experience and navigation, but actual authorization is always enforced by the backend.

---

## 5. Backend Architecture

The FastAPI backend follows a layered architecture.

```text
                    HTTP Request
                         │
                         ▼
                ┌─────────────────┐
                │     Router      │
                │  API Endpoints  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Dependencies   │
                │ Auth / RBAC     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Service Layer  │
                │ Business Logic  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Data Access     │
                │ SQLAlchemy ORM  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   PostgreSQL    │
                └─────────────────┘
```

### Router Layer

Responsible for:

* Defining HTTP endpoints.
* Parsing requests.
* Request validation.
* Calling service-layer operations.
* Returning appropriate HTTP responses.

### Authentication and Authorization Layer

Responsible for:

* Validating access tokens.
* Identifying the authenticated user.
* Checking account status.
* Enforcing role-based access control.

### Service Layer

Contains application business logic such as:

* Complaint creation.
* Status transitions.
* Complaint history creation.
* Priority updates.
* Overdue detection.
* Category management.
* User management.
* Notice management.
* Dashboard calculations.
* Notification orchestration.

### Data Access Layer

Responsible for:

* SQLAlchemy models.
* Database queries.
* Transactions.
* Relationships.
* Persistence.

### External Service Layer

Responsible for communicating with:

* Image storage provider.
* Email provider.

External service integrations are isolated from the core business logic so they can be replaced without significantly changing the rest of the application.

---

## 6. Backend Modules

The backend will be organized into the following functional modules:

```text
server/app/

├── auth
├── users
├── complaints
├── categories
├── notices
├── dashboard
├── notifications
├── uploads
├── core
└── database
```

### Authentication

Handles:

* Registration.
* Login.
* JWT generation and validation.
* Password hashing.
* Role-based authorization.

### Users

Handles:

* Resident account management.
* Account activation/deactivation.
* User information.

### Complaints

Handles:

* Complaint creation.
* Complaint retrieval.
* Complaint filtering.
* Status updates.
* Priority updates.
* Complaint history.
* Overdue detection.

### Categories

Handles:

* Category creation.
* Category updates.
* Category activation/deactivation.

### Notices

Handles:

* Notice creation.
* Notice updates.
* Notice retrieval.
* Important notices.

### Dashboard

Handles:

* Complaint statistics.
* Status distribution.
* Category distribution.
* Priority distribution.
* Overdue count.

### Notifications

Handles:

* Complaint status-change emails.
* Important-notice emails.

### Uploads

Handles:

* Image validation.
* Image upload.
* Storage URL generation.

---

## 7. Authentication and Authorization Flow

The system uses JWT-based authentication.

### Login Flow

```text
User
 │
 │ Email + Password
 ▼
POST /api/v1/auth/login
 │
 ▼
FastAPI
 │
 ├── Find user
 ├── Check account is ACTIVE
 ├── Verify password
 └── Generate JWT
          │
          ▼
       Frontend
```

The JWT contains the information required to identify the authenticated user.

For protected requests:

```text
Frontend
   │
   │ Authorization: Bearer <JWT>
   ▼
FastAPI
   │
   ▼
JWT Validation
   │
   ▼
User Identification
   │
   ▼
Role / Account Status Check
   │
   ├──────────────┐
   ▼              ▼
RESIDENT         ADMIN
```

Backend authorization determines whether the requested operation is permitted.

---

## 8. Complaint Lifecycle

The complaint lifecycle is:

```text
              ┌─────────────┐
              │    OPEN     │
              └──────┬──────┘
                     │
                     │ Admin starts work
                     ▼
              ┌─────────────┐
              │ IN_PROGRESS │
              └──────┬──────┘
                     │
                     │ Admin resolves
                     ▼
              ┌─────────────┐
              │  RESOLVED   │
              └─────────────┘
```

A complaint may also transition directly:

```text
OPEN → RESOLVED
```

`RESOLVED` is a terminal state.

Every successful status change creates an immutable history record.

```text
Complaint
    │
    ├── Current Status
    │
    └── Status History
          ├── Previous Status
          ├── New Status
          ├── Actor
          ├── Note
          └── Timestamp
```

The complaint update and history creation are performed within the same database transaction.

---

## 9. Overdue Detection

Overdue status is calculated from the complaint creation date.

The backend uses the configured overdue threshold.

Conceptually:

```text
is_overdue =
    complaint.status != RESOLVED
    AND
    current_time > complaint.created_at + threshold
```

The overdue state is calculated dynamically rather than stored permanently.

This prevents stale overdue information and ensures that the result always reflects the current time and configured threshold.

Overdue complaints are exposed through the API and prominently displayed in the admin interface.

---

## 10. Complaint Photo Upload Flow

Residents can optionally attach a photo when creating a complaint.

```text
Resident
   │
   │ Complaint + Image
   ▼
React Frontend
   │
   │ multipart/form-data
   ▼
FastAPI
   │
   ├── Validate file type
   ├── Validate file size
   │
   ▼
Image Storage
   │
   │ Stored image URL
   ▼
FastAPI
   │
   ▼
PostgreSQL
   │
   └── photo_url
```

The actual image binary is stored externally.

PostgreSQL stores only the image URL or storage reference.

Storage credentials remain on the backend and are never exposed to the frontend.

---

## 11. Notification Architecture

Notifications are triggered by important application events.

### Complaint Status Change

```text
Admin
  │
  │ Update Status
  ▼
FastAPI
  │
  ├── Validate transition
  │
  ├── Update complaint
  │
  ├── Create history record
  │
  └── Commit transaction
          │
          ▼
   Notification Service
          │
          ├── Check resident is ACTIVE
          │
          ▼
      Email Provider
          │
          ▼
       Resident
```

### Important Notice

```text
Admin
  │
  │ Create Important Notice
  ▼
FastAPI
  │
  ├── Store notice
  │
  ▼
Notification Service
  │
  ├── Find active residents
  │
  ▼
Email Provider
  │
  ▼
Active Residents
```

Email delivery failures must not roll back successfully completed core database operations.

---

## 12. Notice Board Flow

```text
Admin
  │
  │ Create Notice
  ▼
FastAPI
  │
  ▼
PostgreSQL
  │
  ▼
Notice Board API
  │
  ▼
React Frontend
  │
  ├── Important Notices
  │       ↓
  │    Normal Notices
  │
  ▼
Resident
```

Important notices are displayed before normal notices.

Within the same importance level, newer notices are displayed first.

---

## 13. Dashboard Data Flow

The admin dashboard retrieves aggregated statistics from the backend.

```text
Admin Dashboard
      │
      │ GET /api/v1/admin/dashboard
      ▼
FastAPI
      │
      ▼
Dashboard Service
      │
      ▼
PostgreSQL
      │
      ├── Total Complaints
      ├── Status Distribution
      ├── Category Distribution
      ├── Priority Distribution
      └── Overdue Count
      │
      ▼
   JSON Response
      │
      ▼
React Dashboard
```

Dashboard calculations are performed by the backend rather than transferring all complaint records to the frontend.

---

## 14. Data and External Service Boundaries

The system separates core application data from external service data.

### PostgreSQL stores:

* Users
* Complaint records
* Complaint status history
* Complaint categories
* Notices
* System configuration

### External image storage stores:

* Complaint photos

PostgreSQL stores the corresponding image URL or storage reference.

### Email provider handles:

* Complaint status emails
* Important notice emails

The application stores only the information required for notification processing and auditing.

---

## 15. Deployment Architecture

The frontend and backend are deployed independently.

```text
                         Internet
                            │
               ┌────────────┴────────────┐
               │                         │
               ▼                         ▼
        ┌─────────────┐          ┌─────────────┐
        │   Vercel    │          │   Render /  │
        │   React     │ ───────▶ │   Railway   │
        │  Frontend   │  HTTPS   │   FastAPI   │
        └─────────────┘          └──────┬──────┘
                                        │
                                        ▼
                                ┌──────────────┐
                                │  PostgreSQL  │
                                └──────────────┘

                                ┌──────────────┐
                                │    Image     │
                                │    Storage   │
                                └──────────────┘

                                ┌──────────────┐
                                │ Email Service│
                                └──────────────┘
```

Environment-specific configuration is provided through environment variables.

Secrets are never committed to the repository.

---

## 16. Security Considerations

The system follows the following security principles:

* Passwords are stored using secure password hashing.
* Authentication uses signed access tokens.
* Authorization is enforced on the backend.
* Residents cannot access other residents' complaints.
* Admin-only operations require the `ADMIN` role.
* Inactive users cannot authenticate.
* File uploads are validated.
* External service credentials remain server-side.
* Secrets are stored through environment variables.
* Sensitive information is excluded from application logs.

---

## 17. Architectural Principles

The system follows these principles:

1. **Separation of concerns** — API, business logic, data access, and external services are separated.
2. **Backend-enforced authorization** — frontend restrictions are not treated as security controls.
3. **Database integrity** — relationships and critical operations are protected through database constraints and transactions.
4. **Immutable history** — complaint status history is append-only.
5. **Configurable behavior** — settings such as overdue thresholds and complaint categories can change without modifying core application logic.
6. **Externalized media** — large image files are stored outside PostgreSQL.
7. **Stateless API** — authentication does not depend on server-side session state.
8. **Maintainability** — functionality is organized into clear backend modules.
9. **Scalable deployment** — frontend and backend can be scaled independently.
