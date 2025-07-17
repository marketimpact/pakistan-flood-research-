# Phase 4: Dashboard & Data Collection Commands (TDD)

**Goal:** To build the user-facing dashboard, create efficient data export functionality, and connect the data collection services to management commands.

**Deliverables:**
*   A `dashboard` app with login-protected views.
*   **A memory-efficient CSV export using `StreamingHttpResponse`.**
*   Management commands that act as thin wrappers around the service layer.
*   Fully tested service layer methods for data collection.

| Step | Action (Programmer) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 4.1 | Create `dashboard` App | Create the `dashboard` app. | To Do |
| 4.2 | **Write Failing View Test** | In `dashboard/tests/test_views.py`, write a test that tries to access `/dashboard/`. Assert a 302 redirect. **The test must fail.** | To Do |
| 4.3 | **Write View & URL** | Create the `DashboardView` (`LoginRequiredMixin`) and URL pattern. | To Do |
| 4.4 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
| 4.5 | **Write Failing Export Test** | Write a test for a `/download/{gauge_id}/` view. Assert the response is a `StreamingHttpResponse` with the correct `Content-Type`. **The test must fail.** | To Do |
| 4.6 | **Write Export View** | Create the view using `StreamingHttpResponse` and a generator function that iterates over the queryset with `iterator()`. | To Do |
| 4.7 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
| 4.8 | **Write Failing Command Test** | In `core/tests/test_commands.py`, test the `collect_data` command. Use `mock.patch` to mock the `DataCollectionService`. Assert the service method is called. **The test must fail.** | To Do |
| 4.9 | **Write Command Code** | Create the `collect_data` management command as a thin wrapper around the service. | To Do |
| 4.10 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
| 4.11 | Note on Async Tasks | For now, the cron job is sufficient. If data collection becomes too slow, the next step is to refactor the service call into a Celery task. This is a future enhancement. | Done |
