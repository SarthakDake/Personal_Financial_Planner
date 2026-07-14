"""Unit tests for loan EMI and amortization."""

from financial_engine.calculators.loans import LoanCalculator


def test_emi_formula():
    emi = LoanCalculator.calculate_emi(5_000_000, 0.085, 240)
    assert 40_000 < emi < 50_000


def test_amortization_pays_down():
    schedule = LoanCalculator.amortization_schedule(1_000_000, 0.10, 12)
    assert len(schedule) == 12
    assert schedule.iloc[-1]["closing_balance"] < 1
    assert schedule["interest"].sum() > 0


def test_prepayment_saves_interest():
    result = LoanCalculator.analyze_loan(
        name="Test",
        loan_type="personal",
        principal_outstanding=500_000,
        annual_rate=0.12,
        emi=LoanCalculator.calculate_emi(500_000, 0.12, 36),
        tenure_months=36,
        prepayment=100_000,
    )
    assert result["interest_saved"] > 0
    assert result["months_saved"] > 0
