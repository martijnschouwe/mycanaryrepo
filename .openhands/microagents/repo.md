# Repository Governance & Developer Guidelines (`mycanaryrepo`)

This document defines the architecture, coding standards, and Two-Stage TDD workflow for **mycanaryrepo**. Every contributor and AI agent MUST strictly adhere to these contracts.

---

## 1. Repository Contract Summary (`.openhands/project.json`)

- **Project Name**: `mycanaryrepo`
- **Primary Language**: `Python`
- **Source Directories**: `app/`
- **Protected Test Directories**: `tests/`
- **Test Command**: `pytest -q`
- **Typecheck / Static Check**: `python3 -m compileall -q app tests`
- **Contract Documents**: `.openhands/microagents/repo.md`, `PARITY.md`, `ARCHITECTURE.md`

---

## 2. Two-Stage GitHub Label State Machine (Autonomous TDD)

1. **Stage 1 (`dev-ready` → `tests-ready`) — Worker 1: Test Architect (`gemini-4-argon`)**
   - Reads the GitHub issue and all repository contracts (`.openhands/microagents/repo.md`, `PARITY.md`, `ARCHITECTURE.md`).
   - Exclusively designs and writes unit, boundary, and edge-case tests in `tests/`.
   - **STRICT RULE**: Must **NEVER** write or modify implementation code in `app/`.
   - Commits and pushes failing tests (Red stage) on branch `feat/issue-<nr>` and transitions the issue label from `dev-ready` to `tests-ready`.

2. **Stage 2 (`tests-ready` → `review-ready`) — Worker 2: The Coder (`claude-5-0-sonnet`)**
   - Checks out branch `feat/issue-<nr>`, runs `pytest -q`, and inspects the failing tests in `tests/`.
   - Implements the required Python code in `app/` until `pytest -q` is 100% green.
   - **STRICT IMMUTABILITY RULE**: Must **UNDER NO CIRCUMSTANCES** modify files in `tests/` or weaken test assertions. Enforced by `scripts/verify-tests-untouched.sh`.
   - Opens PR `fix: resolve issue #<nr>` referencing the issue and transitions the label from `tests-ready` to `review-ready`.
