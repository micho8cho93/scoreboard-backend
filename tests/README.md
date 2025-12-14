# Test Suite Documentation

This directory contains the complete test suite for the Real-Time Scoreboard App, organized by development phases following Test-Driven Development (TDD) principles.

## Test Structure

The tests are organized into 7 phases, matching the `test_roadmap.yml`:

### Phase 1: Domain Model Tests (`test_models.py`)
- Validates data models (Sport, Game, Event) before API implementation
- Tests model validation and constraints
- **Status**: Tests are scaffolded and ready to be activated once models are created

### Phase 2: REST API Contract Tests (`test_api.py`)
- Tests REST endpoints: `/sports`, `/games`, `/sports/{sport_id}/games`
- Validates HTTP status codes, response formats, and data contracts
- **Status**: Tests are scaffolded and ready to be activated once API endpoints are created

### Phase 3: Play-By-Play Event API Tests (`test_events.py`)
- Tests event creation endpoint: `/games/{game_id}/events`
- Validates event validation, persistence, and chronological ordering
- **Status**: Tests are scaffolded and ready to be activated once event endpoints are created

### Phase 4: WebSocket Tests (`test_websocket.py`)
- Tests WebSocket connection handling and event broadcasting
- Validates real-time functionality
- **Status**: Tests are scaffolded and ready to be activated once WebSocket endpoints are created

### Phase 5: Integration Tests (`test_integration.py`)
- Tests REST and WebSocket layers working together
- Validates complete game flows and concurrent event handling
- **Status**: Tests are scaffolded and ready to be activated once all components are integrated

### Phase 6: Frontend Contract Tests (`test_frontend.py`)
- Tests frontend UI components using Playwright
- Validates UI behavior against backend contracts
- **Status**: Tests are scaffolded and ready to be activated once frontend is created

### Phase 7: End-to-End Tests (`test_e2e.py`)
- Tests the complete deployed system
- Validates real-time latency and multi-sport scenarios
- **Status**: Tests are scaffolded and ready to be activated once full system is deployed

## Running Tests

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers (for frontend/E2E tests):
```bash
playwright install
```

### Running All Tests

```bash
pytest
```

### Running Tests by Phase

```bash
# Phase 1: Domain Models
pytest tests/test_models.py

# Phase 2: REST API
pytest tests/test_api.py

# Phase 3: Events API
pytest tests/test_events.py

# Phase 4: WebSocket
pytest tests/test_websocket.py

# Phase 5: Integration
pytest tests/test_integration.py

# Phase 6: Frontend
pytest tests/test_frontend.py

# Phase 7: E2E
pytest tests/test_e2e.py
```

### Running Specific Tests

```bash
# Run a specific test by name
pytest tests/test_models.py::TestSportModel::test_sport_model_valid

# Run tests matching a pattern
pytest -k "sport_model"
```

## TDD Workflow

1. **Write a failing test** - Tests are currently scaffolded with `pytest.skip()` placeholders
2. **Remove the skip** - Uncomment the test code and remove `pytest.skip()`
3. **Run the test** - It should fail (red)
4. **Implement minimal code** - Write just enough to make the test pass
5. **Run the test** - It should pass (green)
6. **Refactor** - Improve code while keeping tests green

## Test Configuration

- **Test Database**: In-memory SQLite (fresh database per test)
- **Test Client**: FastAPI TestClient for HTTP requests
- **WebSocket Testing**: FastAPI WebSocket test utilities
- **Frontend Testing**: Playwright with headless Chromium

## Current Status

All test files are created and structured according to the roadmap. Tests are currently skipped (`pytest.skip()`) until the corresponding application code is implemented. As you implement each feature:

1. Remove the `pytest.skip()` call
2. Uncomment the test code
3. Run the test (it should fail)
4. Implement the feature
5. Run the test again (it should pass)

## Notes

- Tests use fixtures defined in `conftest.py` for database and client setup
- Each test is isolated and gets a fresh database
- WebSocket tests use `pytest-asyncio` for async support
- Frontend tests require a running frontend server (configure URL in tests)

