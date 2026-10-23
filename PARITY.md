# Functional Parity & Domain Contract (`mycanaryrepo`)

## 1. Monetary & Numerical Rules
- All monetary values MUST be represented and calculated in **integer cents** (e.g. `1000` = €10.00) or rounded deterministically using **round-half-up** to integer cents.
- Floating-point drift (e.g. `0.1 + 0.2 != 0.3`) is strictly forbidden in outputs.
- Negative prices, negative tax rates, or discounts exceeding 100% MUST be rejected with an explicit validation error (`ValueError` in Python / `Error` in TypeScript).

## 2. Security & Input Hygiene
- String inputs (codes, descriptions, customer fields) must be trimmed and validated.
- Empty or whitespace-only identifiers and XSS/script injection payloads (`<script>`, `javascript:`) must be rejected.

## 3. Discount Calculations (`apply_discount_cents`)
- **Signature**: `def apply_discount_cents(subtotal_cents: int, discount_bps: int) -> int:`
- **Calculation**:
  - `discount_amount_cents = (subtotal_cents * discount_bps + 5000) // 10000` (deterministic integer round-half-up)
  - Returns `subtotal_cents - discount_amount_cents`
- **Validation**:
  - If `subtotal_cents` or `discount_bps` is a `bool` or not an `int`, raise `TypeError` with "subtotal_cents must be an integer" or "discount_bps must be an integer".
  - If `subtotal_cents < 0`, raise `ValueError` with "subtotal_cents cannot be negative".
  - If `discount_bps < 0`, raise `ValueError` with "discount_bps cannot be negative".
  - If `discount_bps > 10000`, raise `ValueError` with "discount_bps cannot exceed 10000".

## 4. Definition of Done
- Every feature or bugfix must have comprehensive unit and boundary tests in `tests/`.
- `pytest -q` must pass 100% with zero modifications to existing or Stage 1 test files during Stage 2.
