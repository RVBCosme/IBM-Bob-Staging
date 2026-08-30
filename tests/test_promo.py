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
