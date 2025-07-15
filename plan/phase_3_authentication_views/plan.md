# Phase 3: User Authentication & Basic Views (TDD)

**Goal:** To implement a secure login system and a dashboard page that displays the collected data.

**Deliverables:**
*   Working login and logout functionality.
*   A dashboard view, protected by login, that lists all gauges.

| Step | Action (Programmer) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 3.1 | **Write Failing View Test** | In `gauges/tests/test_views.py`, write a test that tries to access a `/dashboard/` URL. Assert that the response is a 302 redirect to the login page. **The test must fail** (404, as the URL doesn't exist). | To Do |
| 3.2 | **Write View & URL Code** | Create the `DashboardView` and the corresponding URL pattern. Add the `@login_required` decorator. | To Do |
| 3.3 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
| 3.4 | **Write Content Test** | Write a new test that creates a user, logs them in via the test client, creates a test `Gauge` in the database, and then accesses `/dashboard/`. Assert that the gauge's name appears in the response content. **The test must fail.** | To Do |
| 3.5 | **Implement View Logic** | Update the `DashboardView` to fetch all `Gauge` objects and pass them to a template. Create the template to render the list. | To Do |
| 3.6 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
