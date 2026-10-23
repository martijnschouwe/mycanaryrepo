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


def apply_discount_cents(subtotal_cents: int, discount_percent: int) -> int:
    """Calculate the discounted price in integer cents after applying an integer percentage discount.

    Formula: subtotal_cents - round_half_up(subtotal_cents * discount_percent / 100) using deterministic integer
    arithmetic: (subtotal_cents * discount_percent + 50) // 100 for the discount amount, subtracted from subtotal_cents.
    """
    if isinstance(subtotal_cents, bool) or not isinstance(subtotal_cents, int):
        raise TypeError("subtotal_cents must be an integer")
    if isinstance(discount_percent, bool) or not isinstance(discount_percent, int):
        raise TypeError("discount_percent must be an integer")
    if subtotal_cents < 0:
        raise ValueError("subtotal_cents cannot be negative")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be between 0 and 100 inclusive")

    discount_amount = (subtotal_cents * discount_percent + 50) // 100
    return subtotal_cents - discount_amount
