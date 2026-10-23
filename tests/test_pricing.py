"""Baseline unit tests for app.pricing."""

import pytest

from app.pricing import calculate_subtotal_cents, apply_discount_cents


def test_calculate_subtotal_cents_basic() -> None:
    assert calculate_subtotal_cents(1250, 3) == 3750
    assert calculate_subtotal_cents(0, 5) == 0


def test_calculate_subtotal_cents_rejects_negative() -> None:
    with pytest.raises(ValueError):
        calculate_subtotal_cents(-100, 1)
    with pytest.raises(ValueError):
        calculate_subtotal_cents(100, -2)


def test_apply_discount_cents_basic() -> None:
    """Test standard and boundary case values for apply_discount_cents."""
    # BDD standard example 1
    assert apply_discount_cents(1000, 15) == 850

    # Boundary case: subtotal is 0
    assert apply_discount_cents(0, 0) == 0
    assert apply_discount_cents(0, 50) == 0
    assert apply_discount_cents(0, 100) == 0

    # Boundary case: discount is 0%
    assert apply_discount_cents(100, 0) == 100
    assert apply_discount_cents(1250, 0) == 1250

    # Boundary case: discount is 100%
    assert apply_discount_cents(100, 100) == 0
    assert apply_discount_cents(1250, 100) == 0


def test_apply_discount_cents_rounding() -> None:
    """Test half-way and boundary rounding cases using round-half-up logic."""
    # BDD standard example 2 (half-way round up: 10.5 cents -> 11 cents)
    assert apply_discount_cents(105, 10) == 94

    # 105 * 5 = 525. 525 / 100 = 5.25. Round-half-up to 5.
    assert apply_discount_cents(105, 5) == 100

    # 105 * 15 = 1575. 1575 / 100 = 15.75. Round-half-up to 16.
    assert apply_discount_cents(105, 15) == 89

    # 105 * 25 = 2625. 2625 / 100 = 26.25. Round-half-up to 26.
    assert apply_discount_cents(105, 25) == 79

    # 105 * 35 = 3675. 3675 / 100 = 36.75. Round-half-up to 37.
    assert apply_discount_cents(105, 35) == 68

    # 105 * 45 = 4725. 4725 / 100 = 47.25. Round-half-up to 47.
    assert apply_discount_cents(105, 45) == 58

    # 105 * 55 = 5775. 5775 / 100 = 57.75. Round-half-up to 58.
    assert apply_discount_cents(105, 55) == 47

    # 105 * 95 = 9975. 9975 / 100 = 99.75. Round-half-up to 100.
    assert apply_discount_cents(105, 95) == 5

    # Halfway round up check for .5 cents exactly (e.g., subtotal = 10, discount = 15 -> 1.5 cents -> rounds to 2)
    assert apply_discount_cents(10, 15) == 8


def test_apply_discount_cents_rejects_negative_and_out_of_bounds() -> None:
    """Test that ValueError is raised for negative subtotal or out-of-bounds discount percentage."""
    # Negative subtotal
    with pytest.raises(ValueError):
        apply_discount_cents(-1, 10)
    with pytest.raises(ValueError):
        apply_discount_cents(-100, 0)

    # Negative discount percent
    with pytest.raises(ValueError):
        apply_discount_cents(100, -1)
    with pytest.raises(ValueError):
        apply_discount_cents(100, -50)

    # Discount percent > 100
    with pytest.raises(ValueError):
        apply_discount_cents(100, 101)
    with pytest.raises(ValueError):
        apply_discount_cents(100, 150)


def test_apply_discount_cents_rejects_invalid_types() -> None:
    """Test that TypeError is raised for non-integer inputs (bool, float, str, None)."""
    invalid_inputs = [True, False, 10.5, '10', None, [10], {10: 10}]

    for val in invalid_inputs:
        # Invalid subtotal_cents
        with pytest.raises(TypeError):
            apply_discount_cents(val, 10)  # type: ignore

        # Invalid discount_percent
        with pytest.raises(TypeError):
            apply_discount_cents(100, val)  # type: ignore
