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
