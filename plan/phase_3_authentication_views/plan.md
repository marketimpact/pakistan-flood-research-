# Phase 3: API Development with DRF (TDD)

**Goal:** To build a secure, documented, versioned, and tested API for all core models using Django REST Framework.

**Deliverables:**
*   DRF installed and configured with **throttling and CORS**.
*   **OpenAPI/Swagger documentation** via `drf-spectacular`.
*   Serializers and ViewSets for all core models.
*   Passing API tests ensuring authentication, permissions, throttling, and correct data structures.

| Step | Action (Programmer) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 3.1 | Install Dependencies | `pip install djangorestframework djangorestframework-simplejwt drf-spectacular django-cors-headers` | To Do |
| 3.2 | Configure DRF & CORS | In `settings/base.py`, add `rest_framework`, `drf_spectacular`, and `corsheaders` to `INSTALLED_APPS`. Configure `REST_FRAMEWORK` with default permissions, authentication (JWT), and **throttling rates**. Configure `CORS_ALLOWED_ORIGINS`. | To Do |
| 3.3 | Create `api` App | Create the `api` app to house all API-related code. | To Do |
| 3.4 | **Write Failing Serializer Test** | In `api/tests/test_serializers.py`, write a test that attempts to serialize a `Gauge` object. **The test must fail.** | To Do |
| 3.5 | **Write Serializer** | In `api/serializers.py`, create the `GaugeSerializer`. | To Do |
| 3.6 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
| 3.7 | **Write Failing ViewSet Test** | In `api/tests/test_views.py`, use `APIClient` to `GET /api/v1/gauges/`. Assert a 401 Unauthorized response. **The test must fail** (404, URL doesn't exist). | To Do |
| 3.8 | **Write ViewSet & URL** | In `api/views.py`, create the `GaugeViewSet`. In `api/urls.py`, register it with a router. Add the router and `drf-spectacular` URLs to the main project `urls.py`. | To Do |
| 3.9 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
| 3.10 | Write Authenticated & Throttling Tests | Write new tests that authenticate a user and assert a 200 OK response. Write another test to verify that excessive requests are throttled (429 response). | To Do |
| 3.11 | Repeat TDD for Other Models | Repeat the TDD cycle for `Reading` and `Prediction` serializers and viewsets. | To Do |
