# Society Maintenance Tracker — Requirements

## 1. Project Overview

The Society Maintenance Tracker is a web-based complaint management platform for apartment societies.

The platform allows residents to register, authenticate, raise maintenance complaints with optional photos, and track the progress and history of their complaints.

Administrators can manage complaints, assign priorities, update complaint statuses, monitor overdue complaints, publish notices, and view dashboard statistics.

The system also sends email notifications when complaint statuses change and when important notices are published.

---

## 2. Objectives

The main objectives of the system are:

1. Provide residents with a centralized platform for raising maintenance complaints.
2. Provide residents with visibility into the progress of their complaints.
3. Allow administrators to efficiently manage and prioritize complaints.
4. Maintain a complete history of complaint status changes.
5. Automatically identify overdue complaints.
6. Provide a centralized notice board for society announcements.
7. Notify residents about important complaint and notice updates.
8. Provide administrators with useful complaint statistics and reporting.

---

## 3. User Roles

The system has two roles:

### 3.1 Resident

A resident can:

- Register an account.
- Log in and log out.
- Create maintenance complaints.
- Select a complaint category.
- Provide a complaint description.
- Optionally upload a photo.
- View their own complaints.
- View the complete history of their complaints.
- View society notices.
- Receive email notifications.

### 3.2 Admin

An administrator can:

- Log in and log out.
- View all complaints.
- Filter complaints by category, status, and date.
- Set complaint priority.
- Update complaint status.
- Add notes when changing status.
- View complete complaint history.
- Monitor overdue complaints.
- Configure the overdue threshold.
- Create and manage notices.
- Mark notices as important.
- View dashboard statistics.

---

## 4. Functional Requirements

### FR-01: Resident Registration

The system shall allow a resident to create an account using their name, email address, and password.

The system shall prevent registration using an email address that already exists.

Passwords shall never be stored in plain text.

### FR-02: Authentication

The system shall allow registered users to authenticate securely.

Authenticated requests shall use token-based authentication.

The system shall identify the authenticated user's role.

### FR-03: Role-Based Authorization

The system shall support two roles:

- Resident
- Admin

Residents shall only be able to access resident-authorized operations.

Administrators shall have access to administrative operations.

A resident shall not be able to perform administrative actions by directly calling the API.

### FR-04: Create Complaint

A resident shall be able to create a complaint containing:

- Category
- Description
- Optional photo

A newly created complaint shall have:

- Status: OPEN
- Priority: MEDIUM
- Creation timestamp

### FR-05: View Complaints

A resident shall be able to view their own complaints.

A resident shall not be able to access complaints belonging to another resident.

An administrator shall be able to view all complaints.

### FR-06: Complaint Details

The system shall provide detailed information for an individual complaint, including:

- Complaint information
- Current status
- Priority
- Photo, if available
- Creation date
- Last updated date
- Resolution date, if resolved
- Complete status history

### FR-07: Complaint Status Lifecycle

A complaint shall support the following statuses:

- OPEN
- IN PROGRESS
- RESOLVED

The supported lifecycle shall be:

OPEN → IN PROGRESS → RESOLVED

A resolved complaint shall be considered closed.

A resolved complaint shall not be reopened.

### FR-08: Complaint Status History

Every complaint status change shall create a history record.

Each history record shall contain:

- Complaint ID
- Previous status
- New status
- Actor who performed the change
- Timestamp
- Optional note

The history shall be immutable after creation.

### FR-09: Complaint Priority

Each complaint shall have one of the following priorities:

- LOW
- MEDIUM
- HIGH

Administrators shall be able to update the priority of a complaint.

### FR-10: Complaint Filtering

Administrators shall be able to filter complaints by:

- Category
- Status
- Date
- Priority

The system shall support sorting for complaint listings.

### FR-11: Overdue Complaint Detection

The system shall identify complaints as overdue when they remain unresolved beyond a configurable number of days.

Resolved complaints shall never be considered overdue.

Overdue complaints shall be prominently surfaced in the administrator interface.

### FR-12: Overdue Threshold

The overdue threshold shall be configurable by an administrator.

The threshold shall be represented in days.

The system shall use the configured threshold when determining whether an unresolved complaint is overdue.

### FR-13: Photo Upload

Residents shall optionally be able to attach a photo to a complaint.

The system shall validate uploaded files based on:

- Supported file types
- Maximum file size

Images shall be stored using external object/image storage.

The database shall store the resulting image URL rather than the image binary itself.

### FR-14: Notice Board

Administrators shall be able to create notices containing:

- Title
- Content
- Important flag
- Creation timestamp

Residents shall be able to view published notices.

Important notices shall be displayed at the top of the notice board.

### FR-15: Email Notifications

The system shall send an email to the relevant resident when:

1. Their complaint status changes.
2. A new important notice is published.

Email delivery shall be handled through an external email service.

### FR-16: Dashboard

Administrators shall have access to a dashboard containing:

- Total complaints
- Complaints by status
- Complaints by category
- Number of overdue complaints
- Priority distribution

---

## 5. Business Rules

- **BR-01:** Only authenticated residents can create complaints.
- **BR-02:** Only administrators can change complaint status.
- **BR-03:** Only administrators can change complaint priority.
- **BR-04:** A new complaint starts with OPEN status.
- **BR-05:**: A new complaint starts with MEDIUM priority.
- **BR-06:** Every status transition must create a history record.
- **BR-07:** Every history record must identify the actor and timestamp.
- **BR-08:** RESOLVED is a terminal state.
- **BR-09:** A resolved complaint cannot become overdue.
- **BR-10:** A complaint is overdue when it remains unresolved beyond the configured threshold.
- **BR-11:** Residents can only access their own complaints.
- **BR-12:** Administrators can access all complaints.
- **BR-13:** Important notices must appear before normal notices.
- **BR-14:** Status changes should trigger email notifications.
- **BR-15:** Publishing an important notice should trigger email notifications.

---

## 6. Non-Functional Requirements

### NFR-01: Security

The application shall securely hash passwords and protect authenticated endpoints using role-based authorization.

### NFR-02: Reliability

Complaint status updates and their corresponding history records shall be stored consistently.

### NFR-03: Maintainability

The backend shall follow a modular architecture separating routing, business logic, database access, and external services.

### NFR-04: Scalability

The application should be deployable as independently scalable frontend and backend services.

### NFR-05: Configuration

Environment-specific configuration and secrets shall be supplied through environment variables.

### NFR-06: API Documentation

The backend API shall provide interactive API documentation.

---

## 7. Out of Scope

The following features are intentionally outside the initial scope:

- Online maintenance fee payment
- Resident-to-resident chat
- Push notifications
- Mobile applications
- Automated complaint assignment to maintenance workers
- AI-based complaint classification
- Multi-society management

These may be considered future enhancements.