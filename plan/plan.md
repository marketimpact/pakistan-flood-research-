# Pakistan Flood Gauge Data Platform - Render Deployment Plan (v3 - Django)

This document outlines the plan for creating and deploying a full-featured data platform on Render using the Django framework. The platform will collect, store, visualize, and export flood gauge data from the Google Flood Hub API for Pakistan.

## 1. Project Goal

The primary goal remains the same: to build a reliable, secure, and user-friendly platform that automates data collection, creates a historical archive, provides secure access with a UI, and enables data export.

## 2. High-Level Architecture

The architecture is simplified by leveraging Django's integrated nature.

1.  **Database:** A persistent **PostgreSQL** database. This is critical for data persistence and is not negotiable.
2.  **Web Application (Django):** A single, monolithic Django application that handles:
    *   **Backend Logic:** All data processing and business logic.
    *   **User Authentication:** Manages user login, logout, and sessions.
    *   **Frontend UI:** Renders HTML pages using the Django Templating Language.
    *   **Admin Panel:** Provides a ready-to-use interface for data management.
3.  **Scheduled Jobs:** Implemented as Django Management Commands and triggered by Render Cron Jobs.

### Technology Stack
- **Language:** Python 3.11+
- **Web Framework:** **Django**
- **Database:** **PostgreSQL** (using Render's managed service)
- **Scheduling:** Render Cron Jobs executing Django Management Commands
- **Deployment Platform:** Render

## 3. Data Model (Django Models)

The database schema will be managed by the Django ORM.

### `User` (Built-in)
We will use Django's built-in `User` model, which already includes fields for `username`, `password`, `is_active`, etc.

### `gauges.Gauge`
- `gauge_id` (CharField, Unique) - The ID from the Google API.
- `site_name`, `river_name` (CharField)
- `latitude`, `longitude` (FloatField)
- `source` (CharField)
- `quality_verified`, `has_model` (BooleanField)
- `created_at`, `updated_at` (DateTimeField, auto-managed)

### `readings.Reading`
- `gauge` (ForeignKey to `gauges.Gauge`)
- `timestamp` (DateTimeField with Timezone)
- `water_level` (FloatField)
- `flood_severity` (CharField)
- `is_flooding` (BooleanField)

### `predictions.Prediction`
- `gauge` (ForeignKey to `gauges.Gauge`)
- `fetched_at` (DateTimeField with Timezone)
- `prediction_for` (DateTimeField with Timezone)
- `predicted_water_level` (FloatField)
- `upper_bound`, `lower_bound` (FloatField, Nullable)

## 4. Key Features & Implementation

### Django Admin Panel
- **Benefit:** Out-of-the-box CRUD (Create, Read, Update, Delete) interface for all our models.
- **Action:** We will register our `Gauge`, `Reading`, and `Prediction` models with the admin site. This will allow administrators to easily view, manage, and debug the collected data without building a custom interface.

### Frontend UI (Django Templates)
- **Login Page:** Use Django's built-in `LoginView`.
- **Dashboard:** A view that lists all `Gauge` objects.
- **Gauge Detail Page:** A view that shows details for a specific `Gauge` and uses a library like Chart.js to visualize its historical `Reading` data.

### Data Export
- **Implementation:** A Django view that queries the `Reading` data for a specific gauge, uses Python's `csv` module to generate a CSV file in memory, and returns it in an `HttpResponse` with the correct headers to trigger a download.

## 5. Core Logic - Django Management Commands

We will create custom management commands for our scheduled tasks. This is the standard Django way to handle such operations.

- **`collect_data` command (`python manage.py collect_data`):**
    - Contains the hourly logic to fetch data from the `floodStatus` and `gaugeModels` APIs and save it to the `Reading` and `Prediction` tables.
- **`update_gauges` command (`python manage.py update_gauges`):**
    - Contains the daily logic to query the Google `gauges` API and update our `Gauge` table.

## 6. Updated Deployment Plan on Render (`render.yaml`)

The `render.yaml` is updated for a standard Django deployment.

```yaml
services:
  # 1. The PostgreSQL Database (Free tier is fine for starting)
  - type: pserv
    name: flood-data-db
    plan: free
    postgresMajorVersion: 14

  # 2. The Django Web Service
  - type: web
    name: flood-data-platform
    env: python
    buildCommand: |
      pip install -r requirements.txt
      python manage.py migrate # Automatically run migrations on deploy
    startCommand: 'gunicorn project.wsgi:application' # Use Gunicorn for production
    envVars:
      - key: DATABASE_URL
        fromService:
          type: pserv
          name: flood-data-db
          property: connectionString
      - key: GOOGLE_API_KEY
        sync: false
      - key: SECRET_KEY # For Django sessions
        sync: false
      - key: WEB_CONCURRENCY
        value: 4

cron:
  # 3. The Hourly Cron Job
  - name: hourly-data-collection
    schedule: '0 * * * *'
    command: 'python manage.py collect_data'
    service:
      name: flood-data-platform

  # 4. The Daily Cron Job
  - name: daily-gauge-update
    schedule: '0 1 * * *'
    command: 'python manage.py update_gauges'
    service:
      name: flood-data-platform
```

### Next Steps
1.  Initialize a new Django project (`django-admin startproject ...`).
2.  Create Django apps for `gauges`, `readings`, and `predictions`.
3.  Define the models in `models.py` for each app.
4.  Implement the `collect_data` and `update_gauges` management commands.
5.  Create the views, templates, and URL patterns for the frontend.
6.  Register models with the Django admin site.
7.  Finalize the `render.yaml` and deploy.
