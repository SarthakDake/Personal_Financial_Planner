"""Currency formatting helpers for Indian Rupee display."""

from __future__ import annotations


def format_inr(amount: float, decimals: int = 0) -> str:
    """Format number in Indian numbering system with ₹ prefix."""
    negative = amount < 0
    amount = abs(amount)
    if decimals > 0:
        s = f"{amount:.{decimals}f}"
        whole, frac = s.split(".")
    else:
        whole = str(int(round(amount)))
        frac = ""

    if len(whole) <= 3:
        formatted = whole
    else:
        last3 = whole[-3:]
        rest = whole[:-3]
        parts = []
        while rest:
            parts.append(rest[-2:])
            rest = rest[:-2]
        formatted = ",".join(reversed(parts)) + "," + last3

    result = f"₹{formatted}"
    if frac:
        result += f".{frac}"
    if negative:
        result = f"-{result}"
    return result


def to_lakhs(amount: float) -> float:
    return amount / 100_000


def to_crores(amount: float) -> float:
    return amount / 10_000_000
