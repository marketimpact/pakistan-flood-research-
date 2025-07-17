# Phase 5: Admin, Deployment & Finalization

**Goal:** To deploy a secure, hardened, and observable application to Render.

**Deliverables:**
*   A secured and customized Django Admin site.
*   A finalized `render.yaml` with **production-grade settings**.
*   The application successfully deployed and running on Render.

| Step | Action (Programmer) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 5.1 | Secure & Customize Admin | Change the default `/admin/` URL. Register all models with the admin site. | To Do |
| 5.2 | Create Health Check | Create a simple `/health/` view that returns a 200 OK response. | To Do |
| 5.3 | **Harden Production Settings** | In `settings/production.py`, add `CONN_MAX_AGE` for connection pooling and additional security headers (`SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_HSTS_SECONDS`, `X_FRAME_OPTIONS`, etc.). | To Do |
| 5.4 | **Configure Static Files** | Install `whitenoise`. Add `whitenoise.middleware.WhiteNoiseMiddleware` to `MIDDLEWARE` in `settings/production.py`. | To Do |
| 5.5 | Finalize `render.yaml` | Create the final `render.yaml` file. Ensure it uses the `production.py` settings file and includes the `collectstatic` command in the `buildCommand`. | To Do |
| 5.6 | Deploy to Render | Commit all code to the GitHub repository. Link the repository to a new Render Blueprint. | To Do |
| 5.7 | Set Production Secrets | In the Render dashboard, set all required environment variables. | To Do |
| 5.8 | Verify Deployment | Verify the public URL, health check, admin panel, and static file serving. | To Do |
| 5.9 | Verify Cron Jobs & Backups | Manually trigger cron jobs. Review Render's documentation to confirm the database backup schedule and procedure. | To Do |
