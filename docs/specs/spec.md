# Spec: SHOP-412 — Promo codes at checkout

## Problem
The cart has no promotional-code support. Add `apply_promos` to compute the
discounted total given a subtotal and a list of promo codes.

---

## Interface

```python
# src/promo.py
def apply_promos(subtotal: float, codes: list[str]) -> float:
    """Return the total to charge after applying all promo codes."""
```

---

## Behaviour

### Valid codes
| Code    | Discount              |
|---------|-----------------------|
| `SAVE20` | 20 % off the subtotal |
| `TENOFF` | $10.00 off            |

### Rules
1. Any code not in the table above raises `ValueError`.
2. Codes are matched **case-sensitively** — only the exact uppercase form is valid.
3. Passing the same code more than once in `codes` raises `ValueError` (a code may be used once per order).
4. An empty `codes` list is valid; the subtotal is returned unchanged.
5. When multiple codes are provided, **percentage discounts are applied first**, then fixed-amount discounts.
6. The total is clamped to a minimum of `0.00` — it never goes negative.
7. The returned total is rounded to the cent (`round(result, 2)`).

### Worked examples

| subtotal | codes | total |
|----------|-------|-------|
| `100.00` | `["SAVE20"]` | `80.00` |
| `100.00` | `["TENOFF"]` | `90.00` |
| `100.00` | `["SAVE20", "TENOFF"]` | `70.00` |
| `100.00` | `["TENOFF", "SAVE20"]` | `70.00` (order in list doesn't matter; % first) |
| `8.00`   | `["SAVE20", "TENOFF"]` | `0.00` (clamped) |
| `50.00`  | `[]` | `50.00` |
| `50.00`  | `["SAVE20", "SAVE20"]` | raises `ValueError` |
| `50.00`  | `["BOGUS"]` | raises `ValueError` |

---

## Assumptions
1. `subtotal` is a non-negative `float`; the function does not validate it.
2. Codes are case-sensitive — `save20` and `Save20` are invalid; only `SAVE20` is valid.
3. `src/promo.py` is a new file; `src/cart.py` is untouched.
4. No other valid codes exist beyond `SAVE20` and `TENOFF`.

---

## Out of scope
- Persisting or logging promo-code usage across orders.
- Adding new codes dynamically (no registry or configuration).
- Validating or computing `subtotal` (that is `cart.subtotal`'s responsibility).
- Any HTTP, CLI, or UI surface.
