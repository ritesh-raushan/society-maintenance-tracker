# Society Maintenance Tracker — Database Design

## 1. Database Overview

The Society Maintenance Tracker uses PostgreSQL as its primary relational database.

PostgreSQL is suitable for the system because the application contains strongly related entities such as users, complaints, complaint history, categories, and notices.

The database is designed to provide:

* Referential integrity
* Transactional consistency
* Immutable complaint history
* Efficient filtering and reporting
* Configurable application settings
* Soft deactivation of users and categories

Primary keys use UUIDs.

---

## 2. Entity Overview

The database consists of the following core entities:

1. `users`
2. `categories`
3. `complaints`
4. `complaint_status_history`
5. `notices`
6. `system_settings`

---

## 3. Entity Relationship Diagram

```text
                         ┌──────────────────────┐
                         │        USERS         │
                         ├──────────────────────┤
                         │ id PK (UUID)         │
                         │ name                 │
                         │ email UNIQUE         │
                         │ password_hash        │
                         │ role                 │
                         │ is_active            │
                         │ created_at           │
                         │ updated_at           │
                         └──────────┬───────────┘
                                    │
                      ┌─────────────┴─────────────┐
                      │                           │
                     1:N                         1:N
                      │                           │
                      ▼                           ▼
             ┌─────────────────┐         ┌─────────────────┐
             │    COMPLAINTS   │         │     NOTICES     │
             ├─────────────────┤         ├─────────────────┤
             │ id PK (UUID)    │         │ id PK (UUID)    │
             │ resident_id FK  │         │ admin_id FK     │
             │ category_id FK  │         │ title           │
             │ description     │         │ content         │
             │ photo_url       │         │ is_important    │
             │ status          │         │ created_at      │
             │ priority        │         │ updated_at      │
             │ created_at      │         └─────────────────┘
             │ updated_at      │
             │ resolved_at     │
             └───────┬─────────┘
                     │
                    1:N
                     │
                     ▼
          ┌──────────────────────────┐
          │ COMPLAINT_STATUS_HISTORY │
          ├──────────────────────────┤
          │ id PK (UUID)             │
          │ complaint_id FK          │
          │ actor_id FK              │
          │ old_status              │
          │ new_status              │
          │ note                    │
          │ created_at              │
          └──────────────────────────┘


             ┌──────────────────┐
             │    CATEGORIES    │
             ├──────────────────┤
             │ id PK (UUID)     │
             │ name UNIQUE      │
             │ description      │
             │ is_active        │
             │ created_at       │
             │ updated_at       │
             └────────┬─────────┘
                      │
                     1:N
                      │
                      ▼
                  COMPLAINTS


             ┌──────────────────────┐
             │   SYSTEM_SETTINGS    │
             ├──────────────────────┤
             │ id PK (UUID)         │
             │ key UNIQUE           │
             │ value                │
             │ updated_by FK        │
             │ updated_at           │
             └──────────────────────┘
```

---

# 4. Users Table

## Purpose

Stores authentication, authorization, and account status information for residents and administrators.

### Schema

| Column          | Type         | Constraints            | Description              |
| --------------- | ------------ | ---------------------- | ------------------------ |
| `id`            | UUID         | PK                     | Unique user identifier   |
| `name`          | VARCHAR(100) | NOT NULL               | User's name              |
| `email`         | VARCHAR(255) | UNIQUE, NOT NULL       | Login email              |
| `password_hash` | VARCHAR(255) | NOT NULL               | Securely hashed password |
| `role`          | ENUM         | NOT NULL               | `RESIDENT` or `ADMIN`    |
| `is_active`     | BOOLEAN      | NOT NULL, DEFAULT TRUE | Account status           |
| `created_at`    | TIMESTAMPTZ  | NOT NULL               | Account creation time    |
| `updated_at`    | TIMESTAMPTZ  | NOT NULL               | Last update time         |

### Account Lifecycle

```text
ACTIVE
  │
  │ Admin deactivates
  ▼
INACTIVE
```

An inactive user is not deleted.

Historical complaints and audit records remain associated with the user.

### Constraints

* `email` must be unique.
* `role` must be either `RESIDENT` or `ADMIN`.
* `is_active` defaults to `TRUE`.
* Passwords are stored only as hashes.

---

# 5. Categories Table

## Purpose

Stores configurable complaint categories.

Categories are intentionally stored separately from complaints so new categories can be added without modifying application code.

### Schema

| Column        | Type         | Constraints            | Description                  |
| ------------- | ------------ | ---------------------- | ---------------------------- |
| `id`          | UUID         | PK                     | Unique category identifier   |
| `name`        | VARCHAR(100) | UNIQUE, NOT NULL       | Category name                |
| `description` | TEXT         | NULL                   | Optional description         |
| `is_active`   | BOOLEAN      | NOT NULL, DEFAULT TRUE | Whether category can be used |
| `created_at`  | TIMESTAMPTZ  | NOT NULL               | Creation time                |
| `updated_at`  | TIMESTAMPTZ  | NOT NULL               | Last update time             |

### Example Categories

```text
Plumbing
Electrical
Cleaning
Security
Water Supply
Parking
Lift
Other
```

These are examples rather than fixed application values.

### Category Lifecycle

```text
ACTIVE
  │
  │ Admin deactivates
  ▼
INACTIVE
```

Inactive categories cannot be selected for new complaints.

Existing complaints retain their original category.

---

# 6. Complaints Table

## Purpose

Stores the current state and primary information of each maintenance complaint.

### Schema

| Column        | Type        | Constraints                  | Description                    |
| ------------- | ----------- | ---------------------------- | ------------------------------ |
| `id`          | UUID        | PK                           | Unique complaint identifier    |
| `resident_id` | UUID        | FK → users.id, NOT NULL      | Resident who created complaint |
| `category_id` | UUID        | FK → categories.id, NOT NULL | Complaint category             |
| `description` | TEXT        | NOT NULL                     | Complaint description          |
| `photo_url`   | TEXT        | NULL                         | External image URL             |
| `status`      | ENUM        | NOT NULL                     | Current complaint status       |
| `priority`    | ENUM        | NOT NULL                     | Complaint priority             |
| `created_at`  | TIMESTAMPTZ | NOT NULL                     | Complaint creation time        |
| `updated_at`  | TIMESTAMPTZ | NOT NULL                     | Last modification time         |
| `resolved_at` | TIMESTAMPTZ | NULL                         | Resolution time                |

### Status Values

```text
OPEN
IN_PROGRESS
RESOLVED
```

### Priority Values

```text
LOW
MEDIUM
HIGH
```

### Default Values

New complaints are created with:

```text
status   = OPEN
priority = MEDIUM
```

### Resolution

When a complaint is marked `RESOLVED`:

```text
resolved_at = current timestamp
```

For unresolved complaints:

```text
resolved_at = NULL
```

---

# 7. Complaint Status History Table

## Purpose

Stores an immutable audit trail of every complaint status transition.

The current status is stored in `complaints`, while the historical transitions are stored separately.

### Schema

| Column         | Type        | Constraints        | Description             |
| -------------- | ----------- | ------------------ | ----------------------- |
| `id`           | UUID        | PK                 | Unique history record   |
| `complaint_id` | UUID        | FK → complaints.id | Related complaint       |
| `actor_id`     | UUID        | FK → users.id      | User who changed status |
| `old_status`   | ENUM        | NOT NULL           | Previous status         |
| `new_status`   | ENUM        | NOT NULL           | New status              |
| `note`         | TEXT        | NULL               | Optional admin note     |
| `created_at`   | TIMESTAMPTZ | NOT NULL           | Time of transition      |

### Example

A complaint may produce:

```text
History #1
OPEN → IN_PROGRESS
Actor: Admin
Note: "Maintenance team assigned"
Time: 2026-08-20 10:30

History #2
IN_PROGRESS → RESOLVED
Actor: Admin
Note: "Issue fixed"
Time: 2026-08-21 16:45
```

History records are append-only and must not be edited or deleted through normal application operations.

---

# 8. Notices Table

## Purpose

Stores society announcements published by administrators.

### Schema

| Column         | Type         | Constraints             | Description              |
| -------------- | ------------ | ----------------------- | ------------------------ |
| `id`           | UUID         | PK                      | Unique notice identifier |
| `admin_id`     | UUID         | FK → users.id, NOT NULL | Admin who created notice |
| `title`        | VARCHAR(200) | NOT NULL                | Notice title             |
| `content`      | TEXT         | NOT NULL                | Notice content           |
| `is_important` | BOOLEAN      | NOT NULL, DEFAULT FALSE | Important/pinned status  |
| `created_at`   | TIMESTAMPTZ  | NOT NULL                | Creation time            |
| `updated_at`   | TIMESTAMPTZ  | NOT NULL                | Last update time         |

### Ordering

Notices should be returned in the following order:

1. Important notices first.
2. Newer notices before older notices within the same importance level.

Conceptually:

```text
ORDER BY is_important DESC, created_at DESC
```

---

# 9. System Settings Table

## Purpose

Stores configurable application-level settings that should be managed through the application rather than hard-coded.

### Schema

| Column       | Type         | Constraints      | Description               |
| ------------ | ------------ | ---------------- | ------------------------- |
| `id`         | UUID         | PK               | Unique setting identifier |
| `key`        | VARCHAR(100) | UNIQUE, NOT NULL | Setting name              |
| `value`      | VARCHAR(255) | NOT NULL         | Setting value             |
| `updated_by` | UUID         | FK → users.id    | Admin who changed setting |
| `updated_at` | TIMESTAMPTZ  | NOT NULL         | Last update time          |

### Initial Setting

```text
overdue_threshold_days
```

Example:

```text
key   = overdue_threshold_days
value = 3
```

The application validates that the configured threshold is a positive number.

---

# 10. Relationships

### User → Complaints

One resident can create many complaints.

```text
users 1 ───────── N complaints
```

### User → Complaint History

One user can perform many status changes.

```text
users 1 ───────── N complaint_status_history
```

### User → Notices

One administrator can create many notices.

```text
users 1 ───────── N notices
```

### User → System Settings

An administrator can update many settings.

```text
users 1 ───────── N system_settings
```

### Category → Complaints

One category can be associated with many complaints.

```text
categories 1 ───────── N complaints
```

### Complaint → Status History

One complaint can have many status history records.

```text
complaints 1 ───────── N complaint_status_history
```

---

# 11. Foreign Key Behavior

The database should preserve historical data.

Recommended behavior:

### User deletion

Users should not normally be physically deleted.

Account deactivation should be used instead.

### Category deletion

Categories should not normally be physically deleted.

Categories should be deactivated instead.

### Complaint deletion

Complaints should not be casually deleted because they represent maintenance records and their history forms an audit trail.

If deletion is ever required, it should be an explicitly controlled administrative operation.

---

# 12. Indexing Strategy

Indexes should be added to fields frequently used for filtering, joins, and sorting.

Recommended indexes include:

### Users

```text
users.email
users.role
users.is_active
```

### Complaints

```text
complaints.resident_id
complaints.category_id
complaints.status
complaints.priority
complaints.created_at
```

### Complaint History

```text
complaint_status_history.complaint_id
complaint_status_history.actor_id
complaint_status_history.created_at
```

### Notices

```text
notices.is_important
notices.created_at
```

### System Settings

```text
system_settings.key
```

Composite indexes can be introduced later based on actual query patterns.

---

# 13. Data Integrity

The database shall enforce:

* Primary key constraints.
* Foreign key constraints.
* Unique email addresses.
* Unique category names.
* Unique system setting keys.
* Non-null constraints for required fields.
* Valid role values.
* Valid complaint status values.
* Valid complaint priority values.

Critical complaint status updates and history creation shall be performed within a single database transaction.

---

# 14. Overdue Detection and Database

The database does not store a permanent `is_overdue` column.

Overdue status is derived using:

```text
complaint.status != RESOLVED
AND
current_time > complaint.created_at + configured_threshold
```

This ensures overdue status remains accurate as time passes.

The database provides the following fields required for the calculation:

```text
complaints.status
complaints.created_at

system_settings.overdue_threshold_days
```

---

# 15. Database Design Principles

The database follows these principles:

1. **Normalization** — Related entities are stored separately to reduce duplication.
2. **Referential integrity** — Foreign keys maintain valid relationships.
3. **Soft deactivation** — Users and categories are deactivated rather than deleted.
4. **Immutable history** — Complaint history is append-only.
5. **Transactional consistency** — Complaint state and history changes are committed atomically.
6. **External media storage** — Image binaries are not stored in PostgreSQL.
7. **Extensibility** — Categories and system settings can change without modifying the database schema.
8. **Auditability** — Important state changes retain actor and timestamp information.
