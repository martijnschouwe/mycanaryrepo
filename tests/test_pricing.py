"""Baseline and feature unit tests for app.pricing."""

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
    # 5% discount on 1000 cents (10.00) -> 950 cents
    assert apply_discount_cents(1000, 500) == 950
    # 0% discount
    assert apply_discount_cents(1000, 0) == 1000
    # 100% discount
    assert apply_discount_cents(1000, 10000) == 0
    # Zero subtotal
    assert apply_discount_cents(0, 500) == 0
    # Zero subtotal and zero discount
    assert apply_discount_cents(0, 0) == 0


def test_apply_discount_cents_rounding() -> None:
    # Half-up rounding boundary checks:
    # 125 cents subtotal, discount_bps = 375 (3.75%):
    # Mathematically: 125 * 0.0375 = 4.6875 -> rounded to 5 cents. Return 125 - 5 = 120.
    assert apply_discount_cents(125, 375) == 120

    # 125 cents subtotal, discount_bps = 120 (1.2%):
    # Mathematically: 125 * 0.012 = 1.5 -> rounded to 2 cents. Return 125 - 2 = 123.
    assert apply_discount_cents(125, 120) == 123

    # 125 cents subtotal, discount_bps = 40 (0.4%):
    # Mathematically: 125 * 0.004 = 0.5 -> rounded to 1 cent. Return 125 - 1 = 124.
    assert apply_discount_cents(125, 40) == 124

    # 125 cents subtotal, discount_bps = 39 (0.39%):
    # Mathematically: 125 * 0.0039 = 0.4875 -> rounded to 0 cents. Return 125 - 0 = 125.
    assert apply_discount_cents(125, 39) == 125


def test_apply_discount_cents_large_values() -> None:
    # Large subtotal
    assert apply_discount_cents(100000000, 1500) == 85000000
    # Large subtotal with 100% discount
    assert apply_discount_cents(100000000, 10000) == 0


def test_apply_discount_cents_type_validation() -> None:
    # Reject non-integers and booleans with TypeError and precise error messages
    invalid_inputs = [10.5, '1000', [1000], (1000,), {1000}, None, True, False]

    for val in invalid_inputs:
        with pytest.raises(TypeError) as exc_info:
            apply_discount_cents(val, 500)
        assert 'subtotal_cents must be an integer' in str(exc_info.value)

        with pytest.raises(TypeError) as exc_info:
            apply_discount_cents(1000, val)
        assert 'discount_bps must be an integer' in str(exc_info.value)


def test_apply_discount_cents_range_validation() -> None:
    # Negative subtotal
    with pytest.raises(ValueError) as exc_info:
        apply_discount_cents(-1, 500)
    assert 'subtotal_cents cannot be negative' in str(exc_info.value)

    # Negative discount
    with pytest.raises(ValueError) as exc_info:
        apply_discount_cents(1000, -1)
    assert 'discount_bps cannot be negative' in str(exc_info.value)

    # Discount exceeding 100% (10000 bps)
    with pytest.raises(ValueError) as exc_info:
        apply_discount_cents(1000, 10001)
    assert 'discount_bps cannot exceed 10000' in str(exc_info.value)
