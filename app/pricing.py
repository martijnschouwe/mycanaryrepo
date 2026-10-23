"""Core pricing utilities (integer cents)."""


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


def apply_discount_cents(subtotal_cents: int, discount_bps: int) -> int:
    """Apply discount in basis points (bps) to subtotal in cents with round-half-up math."""
    if isinstance(subtotal_cents, bool) or not isinstance(subtotal_cents, int):
        raise TypeError("subtotal_cents must be an integer")
    if isinstance(discount_bps, bool) or not isinstance(discount_bps, int):
        raise TypeError("discount_bps must be an integer")
    if subtotal_cents < 0:
        raise ValueError("subtotal_cents cannot be negative")
    if discount_bps < 0:
        raise ValueError("discount_bps cannot be negative")
    if discount_bps > 10000:
        raise ValueError("discount_bps cannot exceed 10000")

    discount_amount_cents = (subtotal_cents * discount_bps + 5000) // 10000
    return subtotal_cents - discount_amount_cents
