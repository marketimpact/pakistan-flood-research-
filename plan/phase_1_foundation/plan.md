# Phase 1: Project Foundation & Core Models (TDD)

**Goal:** To have a functional local Django project with a connected database and fully defined, tested, and migrated data models.

**Deliverables:**
*   A new Django project and associated apps.
*   Passing unit tests for all data models.
*   A successful initial database migration.

| Step | Action (Programmer) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 1.1 | Initialize Project | Create a new Django project and apps (`gauges`, `readings`, `predictions`). | To Do |
| 1.2 | Configure Database | Update `settings.py` to connect to the Render PostgreSQL database using the provided `DATABASE_URL`. | To Do |
| 1.3 | **Write Failing Model Test** | In `gauges/tests.py`, write a test `test_create_gauge` that attempts to create a `Gauge` object. **Run the test; it must fail** because the model doesn't exist. | To Do |
| 1.4 | **Write Model Code** | In `gauges/models.py`, define the `Gauge` model according to the v3 plan. | To Do |
| 1.5 | **Run Test to Pass** | **Run the test again; it must now pass.** | To Do |
| 1.6 | Repeat TDD Cycle | Repeat steps 1.3-1.5 for the `Reading` and `Prediction` models in their respective apps. | To Do |
| 1.7 | Verify & Migrate | Run `makemigrations` and `migrate`. The process should complete without errors. | To Do |
