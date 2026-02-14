# Multi-Tenancy & Authentication Refactor

We have successfully transformed the backend into a **production-grade, multi-tenant system** inspired by Jira.

## Architectural Changes

### Before
*   Users had a simple text field for "organisation".
*   No real separation of data; "Google" was just a string.
*   Projects were loosely coupled.

### After (Jira Architecture)
1.  **Strict Hierarchy**: User -> belongs to -> Organization -> owns -> Projects.
2.  **Scalable**: A user can belong to multiple organizations (e.g., "Personal", "Work", "Consulting").
3.  **Secure**:
    *   **Authentication**: Bearer Token (JWT) required for all actions.
    *   **Authorization**: API checks if you actually belong to the Org before letting you add projects.

## Key File Changes

### 1. New Core Models (The Foundation)
*   `models/organization.py`: Defines the **Organization** (Workspace) entity.
*   `models/user_organization.py`: Manages **Memberships** (User <-> Organization) and Roles (Admin/Member).

### 2. Modified Models
*   `models/user.py`:
    *   **Removed**: `organisation` (text column).
    *   **Added**: Relationships to `Organization` and `UserOrganization`.
*   `models/project.py`:
    *   **Added**: `organization_id` (Projects now belong to workspaces, not just users).

### 3. New & Updated APIs
*   `apis/auth.py`: New **OAuth2 Login** endpoint (returns JWT tokens).
*   `apis/organizations.py`: Endpoints to Create, List, and Get Organizations.
*   `apis/users.py`:
    *   Updated `create_user`: Automatically creates a "Personal Workspace" on signup.
    *   Fixed `TypeError` by handling the deprecated `organisation` field safely.
*   `apis/projects.py`:
    *   **Security Update**: `create_project` now enforces that you must be a member of the Organization to create a project there.
*   `main.py`: Registered the new `auth` and `organization` routers.

### 4. Security & Configuration
*   `core/config.py`: Centralized settings (Secret Keys, DB URL).
*   `core/security.py`: Password hashing and Token generation logic.
*   `apis/dependencies.py`: `get_current_user` dependency to protect routes.

## How to Run & Verify

### 1. Database Setup
```bash
python3 -m poetry run python3 reset_db_tools.py # Resets schema (Required for major changes)
```

### 2. Start Server
```bash
python3 -m poetry run uvicorn main:app --reload
```
