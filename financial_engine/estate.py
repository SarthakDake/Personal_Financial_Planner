"""Estate planning checklist generator."""

from __future__ import annotations

from typing import Any

from financial_engine.models import ClientFinancialProfile, MaritalStatus


def generate_estate_checklist(profile: ClientFinancialProfile) -> list[dict[str, Any]]:
    """
    Produce a personalized estate planning checklist.

    Items are recommendations — status defaults to pending since the system
    does not store legal document completion unless provided.
    """
    has_spouse = profile.personal.marital_status == MaritalStatus.MARRIED
    has_children = profile.personal.children > 0
    has_real_estate = profile.assets.real_estate > 0
    has_significant_assets = profile.assets.total_assets > 5_000_000

    checklist = [
        {
            "item": "Will",
            "priority": "high",
            "applicable": True,
            "description": "Execute a registered Will covering all assets and guardianship wishes.",
            "status": "pending",
        },
        {
            "item": "Nominee updates",
            "priority": "high",
            "applicable": True,
            "description": (
                "Update nominees across bank accounts, demat, mutual funds, EPF, NPS, "
                "insurance, and PPF."
            ),
            "status": "pending",
        },
        {
            "item": "Power of Attorney",
            "priority": "medium",
            "applicable": True,
            "description": "Consider a Durable Power of Attorney for financial decisions if incapacitated.",
            "status": "pending",
        },
        {
            "item": "Healthcare directive",
            "priority": "medium",
            "applicable": True,
            "description": "Prepare a living will / advance medical directive.",
            "status": "pending",
        },
        {
            "item": "Joint ownership review",
            "priority": "medium",
            "applicable": has_spouse,
            "description": "Review joint holding vs. either-or-survivor for bank and property titles.",
            "status": "pending",
        },
        {
            "item": "Guardian nomination for minors",
            "priority": "high",
            "applicable": has_children,
            "description": "Nominate a guardian for minor children in the Will.",
            "status": "pending",
        },
        {
            "item": "Property title & succession",
            "priority": "high",
            "applicable": has_real_estate,
            "description": "Ensure clear title documents and succession plan for real estate.",
            "status": "pending",
        },
        {
            "item": "Hindu Undivided Family / Trust review",
            "priority": "low",
            "applicable": has_significant_assets,
            "description": "Evaluate trust structures for estate efficiency if net worth is substantial.",
            "status": "pending",
        },
        {
            "item": "Digital asset inventory",
            "priority": "medium",
            "applicable": True,
            "description": "Maintain an encrypted inventory of digital accounts, crypto, and passwords for heirs.",
            "status": "pending",
        },
        {
            "item": "Life insurance alignment",
            "priority": "high",
            "applicable": True,
            "description": "Ensure life cover and nominees align with estate distribution intent.",
            "status": "pending",
        },
        {
            "item": "Business succession plan",
            "priority": "high",
            "applicable": profile.income.business_income_annual > 0,
            "description": "Document business succession, shareholding, and key-person insurance.",
            "status": "pending",
        },
        {
            "item": "Annual estate review",
            "priority": "medium",
            "applicable": True,
            "description": "Review estate documents annually or after major life events.",
            "status": "pending",
        },
    ]
    return [c for c in checklist if c["applicable"]]
