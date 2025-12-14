This document instructs an agentic LLM on how to:

Design tests before writing application code

Use tests as the primary contract

Build the application incrementally while ensuring:

Functional correctness

Real-time guarantees

Stable data contracts

Frontend/backend interoperability

No production code should be written unless a failing test exists first.

Testing Philosophy & Constraints
1 TDD Rules (Strict)

Write a test that fails

Implement the minimal functionality to pass the test

Refactor only when tests remain green

Never write logic without a test that requires it

2 Test Categories (In Order of Importance)

Contract Tests (API shape and data guarantees)

Domain Logic Tests

Integration Tests

Real-Time / WebSocket Tests

Frontend Contract Tests

End-to-End (E2E) Scenarios

Test Infrastructure Setup (First Action)
1 Backend Test Stack

Test runner: Pytest

HTTP client: FastAPI TestClient

Async support: pytest-asyncio

Database: in-memory or isolated test DB

WebSocket client: FastAPI WebSocket test utilities

2 Frontend Test Stack

Headless browser (Playwright or equivalent)

Contract validation via mocked backend responses

Snapshot or DOM assertion testing
