# SHOP-412 Promo Codes — Spec Summary

Feature: `apply_promos(subtotal: float, codes: list[str]) -> float` in `src/promo.py`.

## Valid codes
| Code    | Discount          |
|---------|-------------------|
| SAVE20  | 20% off subtotal  |
| TENOFF  | $10.00 off        |

## Rules
1. Unknown code → `ValueError`.
2. Duplicate code in a single call → `ValueError`.
3. Case-sensitive: only exact uppercase form is valid.
4. Empty list → subtotal returned unchanged.
5. Percentage discounts applied **first**, then fixed-amount (regardless of list order).
6. Result clamped to `0.00` (never negative).
7. Result rounded to the cent (`round(result, 2)`).

## Out of scope
- No dynamic code registry, persistence, HTTP/CLI/UI surface.
- `cart.py` / `subtotal()` untouched.
