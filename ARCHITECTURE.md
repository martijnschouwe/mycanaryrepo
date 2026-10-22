# Architecture & Boundaries (`mycanaryrepo`)

## 1. Overview
`mycanaryrepo` is managed by the JustCommerce OpenHands Autonomous Software Factory using a contract-first, Two-Stage TDD workflow.

## 2. Directory Boundaries
- **Implementation Code (`app/`)**:
  All production Python modules and domain logic live strictly inside `app/`.
- **Automated Test Suite (`tests/`)**:
  All unit, boundary, and integration tests live strictly inside `tests/`.
  Files in `tests/` are owned by Stage 1 (Test Architect) and are immutable during Stage 2 (The Coder).

## 3. Core Architectural Invariants
1. **Deterministic Pure Domain Logic**:
   Business calculations, validations, and transformations must be deterministic and free of hidden global state.
2. **Explicit Input Validation**:
   Invalid types, negative quantities/amounts where forbidden, NaN/infinite values, and malformed payloads must raise explicit `ValueError` / `TypeError` (or domain validation errors) rather than silently returning corrupt results.
3. **Zero External Side Effects in Unit Tests**:
   All tests in `tests/` must execute deterministically offline via `pytest -q`.
