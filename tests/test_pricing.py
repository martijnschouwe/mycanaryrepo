"""Baseline unit tests for app.pricing."""

import pytest

from app.pricing import calculate_subtotal_cents


def test_calculate_subtotal_cents_basic() -> None:
    assert calculate_subtotal_cents(1250, 3) == 3750
    assert calculate_subtotal_cents(0, 5) == 0


def test_calculate_subtotal_cents_rejects_negative() -> None:
    with pytest.raises(ValueError):
        calculate_subtotal_cents(-100, 1)
    with pytest.raises(ValueError):
        calculate_subtotal_cents(100, -2)
