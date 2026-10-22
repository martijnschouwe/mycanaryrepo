"""Core pricing utilities (integer cents)."""

from decimal import Decimal, ROUND_HALF_UP
import math


def calculate_subtotal_cents(unit_price_cents: int, quantity: int) -> int:
    """Return subtotal in integer cents for a given unit price and quantity."""
    if isinstance(unit_price_cents, bool) or not isinstance(unit_price_cents, int):
        raise TypeError("unit_price_cents must be an integer")
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise TypeError("quantity must be an integer")
    if unit_price_cents < 0:
        raise ValueError("unit_price_cents cannot be negative")
    if quantity < 0:
        raise ValueError("quantity cannot be negative")
    return unit_price_cents * quantity


def calculate_vat_cents(subtotal_cents: int, vat_rate_percent: float | int) -> int:
    """Calculate the VAT amount in integer cents using round-half-up rounding.

    Raises ValueError for negative inputs or NaN/infinite rates.
    Raises TypeError for invalid input types.
    """
    if isinstance(subtotal_cents, bool) or not isinstance(subtotal_cents, int):
        raise TypeError("subtotal_cents must be an integer")
    if isinstance(vat_rate_percent, bool) or not isinstance(vat_rate_percent, (int, float)):
        raise TypeError("vat_rate_percent must be a float or integer")

    if isinstance(vat_rate_percent, float) and (math.isnan(vat_rate_percent) or math.isinf(vat_rate_percent)):
        raise ValueError("vat_rate_percent cannot be NaN or infinite")

    if subtotal_cents < 0:
        raise ValueError("subtotal_cents cannot be negative")
    if vat_rate_percent < 0:
        raise ValueError("vat_rate_percent cannot be negative")

    subtotal_dec = Decimal(subtotal_cents)
    vat_rate_dec = Decimal(str(vat_rate_percent))

    vat_cents_dec = (subtotal_dec * vat_rate_dec) / Decimal("100")
    rounded_vat_dec = vat_cents_dec.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    return int(rounded_vat_dec)
