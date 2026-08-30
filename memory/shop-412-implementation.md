# SHOP-412 Implementation

File: `src/promo.py`

```python
_PERCENT_CODES = {"SAVE20": 0.20}
_FIXED_CODES   = {"TENOFF": 10.00}

def apply_promos(subtotal: float, codes: list[str]) -> float:
    known = _PERCENT_CODES.keys() | _FIXED_CODES.keys()
    for code in codes:
        if code not in known:
            raise ValueError(f"Unknown promo code: {code!r}")
    if len(codes) != len(set(codes)):
        raise ValueError("Duplicate promo codes are not allowed")
    total = subtotal
    for code in codes:
        if code in _PERCENT_CODES:
            total *= 1 - _PERCENT_CODES[code]
    for code in codes:
        if code in _FIXED_CODES:
            total -= _FIXED_CODES[code]
    return round(max(0.0, total), 2)
```

All 5 plan tasks completed and green. Tests live in `tests/test_promo.py`.
