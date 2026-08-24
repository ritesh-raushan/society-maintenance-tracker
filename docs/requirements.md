# Society Maintenance Tracker — Requirements

## Project Overview

The Society Maintenance Tracker is a web-based platform for apartment societies where residents can raise maintenance complaints, track their progress, and receive updates. Administrators can manage complaints, publish notices, monitor overdue issues, and view complaint analytics.

## Objectives

- Enable residents to raise and track complaints.
- Give admins a centralized complaint management system.
- Maintain a complete complaint history.
- Detect overdue complaints automatically.
- Notify residents about important updates.
- Provide useful dashboard insights.

---

## User Roles

### Resident

- Register and log in.
- Create complaints with an optional photo.
- Select a complaint category.
- View their own complaints and status history.
- View society notices.
- Receive email notifications while their account is active.

### Admin

- View and manage all complaints.
- Update complaint status and priority.
- Manage complaint categories.
- Activate or deactivate resident accounts.
- Configure overdue threshold.
- Create and manage notices.
- View dashboard analytics.

---

## Functional Requirements

### Authentication

- Public registration creates **Resident** accounts only.
- Initial **Admin** account is created through a secure seed/CLI process.
- Inactive users cannot log in.

### Complaint Management

- Residents can create complaints with:
  - Category
  - Description
  - Optional photo
- New complaints start with:
  - Status: `OPEN`
  - Priority: `MEDIUM`
- Residents can only view their own complaints.
- Admins can view, filter, sort, and paginate all complaints.

### Complaint Categories

- Categories are database-driven and configurable.
- Admins can create, update, activate, and deactivate categories.
- Only active categories can be used for new complaints.

### Complaint Lifecycle

Supported statuses:

- `OPEN`
- `IN_PROGRESS`
- `RESOLVED`

Every status change creates an immutable history record containing:

- Previous status
- New status
- Actor
- Timestamp
- Optional note

### Overdue Detection

A complaint becomes overdue when:

- it is not resolved, and
- the configured number of days has passed since `created_at`.

### Notice Board

Admins can publish notices.

Important notices are pinned to the top and trigger email notifications for active residents.

### Dashboard

Admins can view:

- Total complaints
- Complaints by status
- Complaints by category
- Priority distribution
- Overdue complaints

---

## Business Rules

- Only active authenticated residents can create complaints.
- Only admins can update complaint status or priority.
- Resolved complaints cannot be reopened.
- Complaint history is immutable.
- Inactive users retain historical data but cannot log in or receive emails.
- Email failures must not roll back successful complaint updates.

---

## Non-Functional Requirements

- Secure password hashing and JWT authentication.
- Role-based authorization.
- PostgreSQL as the primary database.
- External storage for uploaded images.
- Environment-based configuration.
- Modular backend architecture.
- Interactive API documentation.

---

## Out of Scope

- Maintenance fee payments
- Resident chat
- Mobile apps
- Multi-society support
- AI-based complaint classification
- Automated maintenance staff assignment