"""Tests for percentage ↔ decimal conversion used by forms and API."""

from utils.percent import (
    convert_profile_rates_to_decimal,
    decimal_to_percent,
    percent_to_decimal,
)


def test_percent_to_decimal():
    assert percent_to_decimal(5) == 0.05
    assert percent_to_decimal(8.5) == 0.085
    assert percent_to_decimal(0) == 0.0
    assert percent_to_decimal(None) is None


def test_decimal_to_percent():
    assert decimal_to_percent(0.05) == 5
    assert decimal_to_percent(0.085) == 8.5


def test_convert_profile_rates():
    raw = {
        "loans": [{"name": "Home", "interest_rate_annual": 8.5}],
        "investments": [{"name": "SIP", "expected_return": 12}],
        "goals": [{"name": "Edu", "inflation_rate": 8, "expected_return": 11}],
        "assumptions": {
            "general_inflation": 6,
            "safe_withdrawal_rate": 4,
            "expected_equity_return": 0,
        },
    }
    converted = convert_profile_rates_to_decimal(raw)
    assert converted["loans"][0]["interest_rate_annual"] == 0.085
    assert converted["investments"][0]["expected_return"] == 0.12
    assert converted["goals"][0]["inflation_rate"] == 0.08
    assert converted["assumptions"]["general_inflation"] == 0.06
    assert converted["assumptions"]["safe_withdrawal_rate"] == 0.04
    assert converted["assumptions"]["expected_equity_return"] is None
