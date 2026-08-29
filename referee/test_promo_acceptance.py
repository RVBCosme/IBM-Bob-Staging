"""Hidden acceptance tests. Written BEFORE either A/B leg. Never shown to the agent."""
import pytest
from src.promo import apply_promos


def test_no_codes():
    assert apply_promos(50.0, []) == 50.0


def test_percent_code():
    assert apply_promos(50.0, ["SAVE20"]) == 40.0


def test_fixed_code():
    assert apply_promos(50.0, ["TENOFF"]) == 40.0


def test_stacking_percent_before_fixed():
    assert apply_promos(50.0, ["TENOFF", "SAVE20"]) == 30.0


def test_unknown_code_rejected():
    with pytest.raises(ValueError):
        apply_promos(50.0, ["BOGUS"])


def test_duplicate_code_rejected():
    with pytest.raises(ValueError):
        apply_promos(50.0, ["TENOFF", "TENOFF"])


def test_total_never_negative():
    assert apply_promos(5.0, ["TENOFF"]) == 0.0


def test_rounds_to_cents():
    assert apply_promos(19.99, ["SAVE20"]) == 15.99
