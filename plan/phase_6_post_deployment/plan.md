# Phase 6: Post-Deployment Hardening & Observability

**Goal:** To enhance the deployed application with enterprise-grade monitoring, testing, and operational procedures.

**Deliverables:**
*   Integration with an Application Performance Monitoring (APM) service.
*   A baseline of integration and security tests.
*   Documented operational procedures.

| Step | Action (Programmer / DevOps) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 6.1 | **Integrate APM** | Choose and integrate an APM service like Sentry or New Relic. Configure it in `settings/production.py` to capture errors and performance data. | To Do |
| 6.2 | **Write Integration Tests** | Create a separate test suite using `TransactionTestCase` to test complex workflows that involve multiple components (e.g., API call -> Service -> Database write). | To Do |
| 6.3 | **Perform Security Scan** | Run a security scanner like `bandit` against the codebase. Review and address any reported vulnerabilities. | To Do |
| 6.4 | **Document Rollback Procedure** | Document the process for rolling back to a previous deployment on Render (e.g., by re-deploying a specific Git commit). | To Do |
| 6.5 | **Plan Performance Testing** | Outline a strategy for future performance testing using tools like Locust, focusing on high-traffic API endpoints. | To Do |
| 6.6 | **Configure Email Backend** | Configure a production-grade email backend (e.g., SendGrid, Mailgun) in `settings/production.py` for error notifications and user-related emails. | To Do |
