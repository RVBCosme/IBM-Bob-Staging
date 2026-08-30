"""Promo-code logic for SHOP-412."""

_PERCENT_CODES = {"SAVE20": 0.20}
_FIXED_CODES = {"TENOFF": 10.00}


def apply_promos(subtotal: float, codes: list[str]) -> float:
    """Return subtotal after applying promo codes. Percent discounts are applied first."""
    known = _PERCENT_CODES.keys() | _FIXED_CODES.keys()
    for code in codes:
        if code not in known:
            raise ValueError(f"Unknown promo code: {code!r}")
    if len(codes) != len(set(codes)):
        raise ValueError("Duplicate promo codes are not allowed")
    total = subtotal
    # Apply percent codes first (regardless of input order)
    for code in codes:
        if code in _PERCENT_CODES:
            total *= 1 - _PERCENT_CODES[code]
    # Then apply fixed-amount codes
    for code in codes:
        if code in _FIXED_CODES:
            total -= _FIXED_CODES[code]
    return max(0.0, total)
