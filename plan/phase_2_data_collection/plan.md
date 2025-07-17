# Phase 2: Core Models & Service Layer (TDD)

**Goal:** To define the core data models with best practices and establish the business logic service layer.

**Deliverables:**
*   `Gauge`, `Reading`, and `Prediction` models in the `core` app, with UUIDs, indexes, and choices.
*   Passing unit tests for all core models.
*   The initial `DataCollectionService` file and structure.
*   A successful database migration for the `core` app.

| Step | Action (Programmer) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 2.1 | **Write Failing Model Test** | In `core/tests/test_models.py`, write a test `test_create_gauge` that asserts a `Gauge` can be created with a UUID primary key. **Run the test; it must fail.** | To Do |
| 2.2 | **Write Model Code** | In `core/models.py`, define the `Gauge` model with `UUIDField` as the primary key, `db_index=True` on `gauge_id`, and `choices` for the `source` field. | To Do |
| 2.3 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
| 2.4 | Repeat TDD for Other Models | Repeat steps 2.1-2.3 for the `Reading` and `Prediction` models. | To Do |
| 2.5 | Create Service Layer | Create the `services/` directory and the `data_collection_service.py` file. | To Do |
| 2.6 | **Write Failing Service Test** | In `core/tests/test_services.py`, write a test that calls a `update_gauges_from_api` function in the service. Use `unittest.mock.patch` to mock an external API call. Assert that a `Gauge` object is created. **The test must fail** (function doesn't exist). | To Do |
| 2.7 | **Write Service Function Stub** | Create the `update_gauges_from_api` function in the service file with minimal logic to make the test pass. | To Do |
| 2.8 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
| 2.9 | Verify & Migrate | Run `makemigrations core` and `migrate`. The process should complete without errors. | To Do |