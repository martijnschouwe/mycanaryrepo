# Functional Parity & Domain Contract (`mycanaryrepo`)

## 1. Monetary & Numerical Rules
- All monetary values MUST be represented and calculated in **integer cents** (e.g. `1000` = €10.00) or rounded deterministically using **round-half-up** to integer cents.
- Floating-point drift (e.g. `0.1 + 0.2 != 0.3`) is strictly forbidden in outputs.
- Negative prices, negative tax rates, or discounts exceeding 100% MUST be rejected with an explicit validation error (`ValueError` in Python / `Error` in TypeScript).

## 2. Security & Input Hygiene
- String inputs (codes, descriptions, customer fields) must be trimmed and validated.
- Empty or whitespace-only identifiers and XSS/script injection payloads (`<script>`, `javascript:`) must be rejected.

## 3. Definition of Done
- Every feature or bugfix must have comprehensive unit and boundary tests in `tests/`.
- `pytest -q` must pass 100% with zero modifications to existing or Stage 1 test files during Stage 2.

## 4. Feature Contracts

### Issue #10: feat(pricing): add apply_discount_cents helper in app/pricing.py
- **Target Scope**: `app/pricing.py`, `apply_discount_cents`, `subtotal_cents`, `discount_percent`
- **Implementation**: `app/pricing.py`
- **Unit & Boundary Tests**: `tests/test_pricing.py`
- **Contract Reference**: `PARITY.md`
- Calculates the discounted price in integer cents after applying an integer percentage discount (`0` to `100`) to `subtotal_cents`.
- Both `subtotal_cents` and `discount_percent` MUST be strictly `int` (reject `bool`, `float`, `str`, `None` with `TypeError`).
- `subtotal_cents < 0` MUST raise `ValueError`.
- `discount_percent < 0` or `discount_percent > 100` MUST raise `ValueError`.
