# Phase 2: Data Collection Commands (TDD)

**Goal:** To create the two core management commands that will fetch and save data from the Google APIs.

**Deliverables:**
*   Two Django management commands: `collect_data` and `update_gauges`.
*   Comprehensive unit tests for both commands that **mock the external API calls**.

| Step | Action (Programmer) | Architect's Instructions & TDD Strategy | Status |
| :--- | :--- | :--- | :--- |
| 2.1 | **Write Failing Command Test** | Create `gauges/tests/test_commands.py`. Write a test that calls `management.call_command('update_gauges')` and asserts that a new `Gauge` is created. Use `unittest.mock.patch` to mock `requests.get`. **The test must fail** (command doesn't exist). | To Do |
| 2.2 | **Write Command Code** | Create the `update_gauges` management command file. Write the minimal code to make the test pass, using the mocked API data. | To Do |
| 2.3 | **Run Test to Pass** | **Run the test; it must now pass.** | To Do |
| 2.4 | Refactor & Add Edge Cases | Add tests for API error handling (e.g., what happens on a 500 error?). Refactor the command logic for clarity. | To Do |
| 2.5 | Repeat TDD Cycle | Repeat steps 2.1-2.4 for the `collect_data` command, testing that both `Reading` and `Prediction` objects are created correctly. | To Do |
