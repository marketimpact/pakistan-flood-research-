# Phase 1: Professional Project Setup (TDD)

**Goal:** To establish a production-grade Django project foundation with a custom user model, structured logging, and environment-aware settings.

**Deliverables:**
*   A new Django project with a feature-based app structure (`core`, `users`).
*   A custom `User` model extending `AbstractUser`.
*   A split settings structure (`base.py`, `development.py`, `production.py`).
*   **Structured JSON logging configured.**
*   Passing unit tests for the custom User model.
*   A successful initial database migration.

| Step | Action (Programmer) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 1.1 | Initialize Project | Create a new Django project. Create the `core` and `users` apps. Reorganize into the new directory structure. | To Do |
| 1.2 | Implement Settings Structure | Create the `settings/` directory and split the settings into `base.py`, `development.py`, and `production.py`. | To Do |
| 1.3 | **Configure Logging** | Install `python-json-logger`. In `settings/base.py`, add the `LOGGING` configuration to output structured JSON logs. | To Do |
| 1.4 | **Write Failing User Model Test** | In `users/tests.py`, write a test to create an instance of the custom `User` model. **Run the test; it must fail.** | To Do |
| 1.5 | **Write Custom User Model** | In `users/models.py`, create a `User` model extending `AbstractUser`. | To Do |
| 1.6 | Configure Custom User Model | In `settings/base.py`, set `AUTH_USER_MODEL = 'users.User'`. | To Do |
| 1.7 | **Run Test to Pass** | **Run the test again; it must now pass.** | To Do |
| 1.8 | Verify & Migrate | Run `makemigrations users` and `migrate`. The process should complete without errors. | To Do |
