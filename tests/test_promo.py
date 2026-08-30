"""Tests for SHOP-412 promo-code feature."""
import pytest
from src.promo import apply_promos


# T1: No codes returns subtotal; SAVE20, TENOFF, and both stacked (% first regardless of list order)
def test_apply_promos_basic_cases():
    """T1: core discount scenarios."""
    # empty codes — subtotal unchanged
    assert apply_promos(50.0, []) == 50.0

    # SAVE20: 20% off 50.00 → 40.00
    assert apply_promos(50.0, ["SAVE20"]) == 40.0

    # TENOFF: $10 off 50.00 → 40.00
    assert apply_promos(50.0, ["TENOFF"]) == 40.0

    # both stacked, % applied first regardless of list order
    # SAVE20 first: 50.00 * 0.80 = 40.00, then TENOFF: 40.00 - 10.00 = 30.00
    assert apply_promos(50.0, ["TENOFF", "SAVE20"]) == 30.0


# T2: Unknown or duplicate code raises ValueError
def test_apply_promos_invalid_codes():
    """T2: unknown and duplicate codes must raise ValueError."""
    with pytest.raises(ValueError):
        apply_promos(50.0, ["BOGUS"])

    with pytest.raises(ValueError):
        apply_promos(50.0, ["SAVE20", "SAVE20"])


# T3: Total is clamped to 0.00 — never negative
def test_apply_promos_clamps_to_zero():
    """T3: result is clamped to 0.00 when discount exceeds subtotal."""
    # TENOFF subtracts $10 from a $5 subtotal; result must be 0.00, not -5.00
    assert apply_promos(5.0, ["TENOFF"]) == 0.0
