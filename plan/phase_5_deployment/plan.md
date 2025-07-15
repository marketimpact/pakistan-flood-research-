# Phase 5: Deployment & Finalization

**Goal:** To deploy the fully tested application to Render and configure the production environment.

**Deliverables:**
*   A finalized `render.yaml` file.
*   The application successfully deployed and running on Render.
*   Cron jobs configured and verified.

| Step | Action (Programmer) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 5.1 | Finalize `render.yaml` | Create the final `render.yaml` file as defined in the v3 plan. Ensure the `migrate` command is in the `buildCommand`. | To Do |
| 5.2 | Deploy to Render | Commit all code to a GitHub repository and link it to a new Render Blueprint. | To Do |
| 5.3 | Set Production Secrets | In the Render dashboard, set the environment variables for `SECRET_KEY` and `GOOGLE_API_KEY`. | To Do |
| 5.4 | Verify Deployment | The initial deployment should succeed. Access the public URL and log in. | To Do |
| 5.5 | Verify Cron Jobs | Manually trigger the `hourly-data-collection` cron job from the Render dashboard and check the logs and the database (via the Admin Panel) to confirm that it ran successfully and new data was saved. | To Do |
