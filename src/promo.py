"""Promo-code logic for SHOP-412."""

_PERCENT_CODES = {"SAVE20": 0.20}
_FIXED_CODES = {"TENOFF": 10.00}


def apply_promos(subtotal: float, codes: list[str]) -> float:
    """Return subtotal after applying promo codes. Percent discounts are applied first."""
    total = subtotal
    # Apply percent codes first (regardless of input order)
    for code in codes:
        if code in _PERCENT_CODES:
            total *= 1 - _PERCENT_CODES[code]
    # Then apply fixed-amount codes
    for code in codes:
        if code in _FIXED_CODES:
            total -= _FIXED_CODES[code]
    return total
