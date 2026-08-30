# Plan: SHOP-412 — Promo codes at checkout

Tasks are ordered smallest-to-largest; each maps to exactly one failing test.

- [x] T1: No codes returns subtotal; SAVE20, TENOFF, and both stacked (% first regardless of list order) → test: `apply_promos(50.0, []) == 50.0`, `apply_promos(50.0, ["SAVE20"]) == 40.0`, `apply_promos(50.0, ["TENOFF"]) == 40.0`, `apply_promos(50.0, ["TENOFF", "SAVE20"]) == 30.0`
- [x] T2: Unknown or duplicate code raises `ValueError` → test: two `pytest.raises(ValueError)` blocks — `apply_promos(50.0, ["BOGUS"])` and `apply_promos(50.0, ["SAVE20", "SAVE20"])`
- [x] T3: Total is clamped to `0.00` — never negative → test: `apply_promos(5.0, ["TENOFF"]) == 0.0`
- [ ] T4: Result is rounded to the cent → test: `apply_promos(19.99, ["SAVE20"]) == 15.99`
