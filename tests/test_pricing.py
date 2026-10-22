"""Baseline and comprehensive unit tests for app.pricing and calculate_vat_cents."""

import math
import pytest

from app.pricing import calculate_subtotal_cents, calculate_vat_cents


def test_calculate_subtotal_cents_basic() -> None:
    assert calculate_subtotal_cents(1250, 3) == 3750
    assert calculate_subtotal_cents(0, 5) == 0


def test_calculate_subtotal_cents_rejects_negative() -> None:
    with pytest.raises(ValueError):
        calculate_subtotal_cents(-100, 1)
    with pytest.raises(ValueError):
        calculate_subtotal_cents(100, -2)


# --- Tests for calculate_vat_cents (Issue #1) ---

def test_calculate_vat_cents_scenario_1() -> None:
    """Scenario 1: Successful VAT calculation with standard percentage.
    Given a subtotal_cents of 10000 and a vat_rate_percent of 20.0
    Returned VAT should be 2000 cents.
    """
    assert calculate_vat_cents(10000, 20.0) == 2000


def test_calculate_vat_cents_scenario_2() -> None:
    """Scenario 2: Successful VAT calculation requiring round-half-up (rounding up).
    Given a subtotal_cents of 10005 and a vat_rate_percent of 19.0
    Returned VAT should be 1901 cents (10005 * 0.19 = 1900.95 -> 1901).
    """
    assert calculate_vat_cents(10005, 19.0) == 1901


def test_calculate_vat_cents_scenario_3() -> None:
    """Scenario 3: Successful VAT calculation requiring round-half-up (rounding up from .5+).
    Given a subtotal_cents of 10004 and a vat_rate_percent of 15.5
    Returned VAT should be 1551 cents (10004 * 0.155 = 1550.62 -> 1551).
    """
    assert calculate_vat_cents(10004, 15.5) == 1551


def test_calculate_vat_cents_scenario_4() -> None:
    """Scenario 4: Successful VAT calculation with zero subtotal.
    Given a subtotal_cents of 0 and a vat_rate_percent of 10.0
    Returned VAT should be 0 cents.
    """
    assert calculate_vat_cents(0, 10.0) == 0


def test_calculate_vat_cents_scenario_5() -> None:
    """Scenario 5: Successful VAT calculation with zero VAT rate.
    Given a subtotal_cents of 10000 and a vat_rate_percent of 0.0
    Returned VAT should be 0 cents.
    """
    assert calculate_vat_cents(10000, 0.0) == 0


def test_calculate_vat_cents_scenario_6() -> None:
    """Scenario 6: Negative subtotal_cents input validation.
    Given a subtotal_cents of -500 and a vat_rate_percent of 10.0
    ValueError should be raised.
    """
    with pytest.raises(ValueError):
        calculate_vat_cents(-500, 10.0)


def test_calculate_vat_cents_scenario_7() -> None:
    """Scenario 7: Negative vat_rate_percent input validation.
    Given a subtotal_cents of 10000 and a vat_rate_percent of -5.0
    ValueError should be raised.
    """
    with pytest.raises(ValueError):
        calculate_vat_cents(10000, -5.0)


def test_calculate_vat_cents_exact_half_rounding() -> None:
    """Rigorous boundary/edge cases to ensure round-half-up is strictly used.
    Standard Python round() uses round-half-to-even.
    This test verifies round-half-up for exact 0.5 cents.
    """
    # 70 * 15.0% = 10.5 cents -> rounds to 11
    assert calculate_vat_cents(70, 15.0) == 11
    
    # 50 * 15.0% = 7.5 cents -> rounds to 8
    assert calculate_vat_cents(50, 15.0) == 8
    
    # 30 * 15.0% = 4.5 cents -> rounds to 5
    assert calculate_vat_cents(30, 15.0) == 5
    
    # 10 * 15.0% = 1.5 cents -> rounds to 2
    assert calculate_vat_cents(10, 15.0) == 2
    
    # 4 * 12.5% = 0.5 cents -> rounds to 1
    assert calculate_vat_cents(4, 12.5) == 1

    # 12 * 12.5% = 1.5 cents -> rounds to 2
    assert calculate_vat_cents(12, 12.5) == 2

    # 20 * 12.5% = 2.5 cents -> rounds to 3
    assert calculate_vat_cents(20, 12.5) == 3

    # 28 * 12.5% = 3.5 cents -> rounds to 4
    assert calculate_vat_cents(28, 12.5) == 4

    # 36 * 12.5% = 4.5 cents -> rounds to 5
    assert calculate_vat_cents(36, 12.5) == 5

    # 44 * 12.5% = 5.5 cents -> rounds to 6
    assert calculate_vat_cents(44, 12.5) == 6


def test_calculate_vat_cents_precision_drift_and_boundaries() -> None:
    """Verify that floating point drift is avoided and high precision is supported.
    - 10000 cents with 15.004% VAT: mathematical value 1500.4 cents -> rounds to 1500
    - 10000 cents with 15.005% VAT: mathematical value 1500.5 cents -> rounds to 1501
    - Extremely large subtotal (1 trillion cents) with 21.0% VAT
    - Extremely small but positive VAT rate (0.0001%) with 1,000,000 cents subtotal -> rounds to 1
    """
    assert calculate_vat_cents(10000, 15.004) == 1500
    assert calculate_vat_cents(10000, 15.005) == 1501
    
    assert calculate_vat_cents(1_000_000_000_000, 21.0) == 210_000_000_000
    assert calculate_vat_cents(1_000_000, 0.0001) == 1


def test_calculate_vat_cents_type_validation() -> None:
    """Explicit type validation for subtotal_cents and vat_rate_percent.
    Bools, strings, lists, dicts, None should be rejected with TypeError.
    - subtotal_cents MUST be an integer. Bools or floats must be rejected.
    - vat_rate_percent MUST be float or int. Bools or strings must be rejected.
    """
    invalid_subtotals = [100.5, "100", [100], {"val": 100}, True, False, None]
    for sub in invalid_subtotals:
        with pytest.raises(TypeError):
            calculate_vat_cents(sub, 21.0) # type: ignore

    invalid_vat_rates = ["21.0", [21.0], {"rate": 21.0}, True, False, None]
    for rate in invalid_vat_rates:
        with pytest.raises(TypeError):
            calculate_vat_cents(1000, rate) # type: ignore


def test_calculate_vat_cents_nan_inf_validation() -> None:
    """Special float values like NaN, Inf, and -Inf must raise ValueError."""
    for bad_rate in [float("nan"), float("inf"), float("-inf")]:
        with pytest.raises(ValueError):
            calculate_vat_cents(1000, bad_rate)


def test_calculate_vat_cents_xss_and_malicious_input() -> None:
    """Verify that potentially vulnerable/malicious input payloads raise TypeError."""
    xss_payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert(1)",
        "SELECT * FROM users",
        "",
        "   "
    ]
    for payload in xss_payloads:
        with pytest.raises(TypeError):
            calculate_vat_cents(payload, 20.0) # type: ignore
        with pytest.raises(TypeError):
            calculate_vat_cents(1000, payload) # type: ignore
