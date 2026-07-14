"""Unit tests for time value of money calculations."""

from datetime import date

from financial_engine.calculators.time_value import TimeValueCalculator


def test_future_value():
    fv = TimeValueCalculator.future_value(100000, 0.10, 10)
    assert abs(fv - 259374.246) < 1


def test_present_value():
    pv = TimeValueCalculator.present_value(259374.246, 0.10, 10)
    assert abs(pv - 100000) < 1


def test_real_return_fisher():
    real = TimeValueCalculator.real_return(0.12, 0.06)
    assert abs(real - ((1.12 / 1.06) - 1)) < 1e-9


def test_sip_future_value_positive():
    fv = TimeValueCalculator.sip_future_value(10000, 0.12, 10)
    assert fv > 10000 * 12 * 10
    assert fv < 10000 * 12 * 10 * 2.5


def test_sip_required_for_goal():
    sip = TimeValueCalculator.sip_required_for_goal(5_000_000, 0.12, 10, 0)
    assert sip > 0
    # Verify SIP grows to approximately target
    fv = TimeValueCalculator.sip_future_value(sip, 0.12, 10)
    assert abs(fv - 5_000_000) / 5_000_000 < 0.02


def test_cagr():
    cagr = TimeValueCalculator.cagr(100000, 200000, 7)
    assert abs(cagr - 0.10409) < 0.001


def test_xirr_simple():
    flows = [-100000, 60000, 60000]
    dates = [date(2020, 1, 1), date(2021, 1, 1), date(2022, 1, 1)]
    rate = TimeValueCalculator.xirr(flows, dates)
    assert 0.1 < rate < 0.3


def test_corpus_from_withdrawal():
    corpus = TimeValueCalculator.corpus_from_withdrawal(1200000, 0.04)
    assert corpus == 30_000_000
