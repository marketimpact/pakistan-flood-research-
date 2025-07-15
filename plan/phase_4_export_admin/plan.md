# Phase 4: Data Export & Admin Panel

**Goal:** To allow users to download data as a CSV and to make data manageable for admins.

**Deliverables:**
*   A working CSV download view.
*   All models registered and usable in the Django Admin site.

| Step | Action (Programmer) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 4.1 | **Write Failing Export Test** | Write a test for a `/download/{gauge_id}/` view. Log in a test user, access the URL, and assert that the response has the correct `Content-Type` (`text/csv`) and `Content-Disposition` headers. **The test must fail.** | To Do |
| 4.2 | **Write Export View** | Create the view that generates the CSV response in memory. | To Do |
| 4.3 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
| 4.4 | Register Models in Admin | In the `admin.py` file for each app, register the models (`Gauge`, `Reading`, `Prediction`). | To Do |
| 4.5 | Verify Admin | Create a superuser and log into the admin panel locally to manually verify that all models are present and usable. | To Do |
