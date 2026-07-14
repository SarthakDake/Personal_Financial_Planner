"""
Dark neon-themed multi-page PDF financial plan (ReportLab).

Uses embedded DejaVu fonts so the Indian Rupee symbol (₹) renders correctly.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from financial_engine.models import ClientFinancialProfile
from utils.money import format_inr

# Neon charcoal theme (matches WealthCraft UI)
BG = colors.HexColor("#0D0D0D")
CARD = colors.HexColor("#1A1A1A")
CARD_ALT = colors.HexColor("#141414")
CYAN = colors.HexColor("#00D1FF")
CYAN_DIM = colors.HexColor("#00A3FF")
TEAL = colors.HexColor("#14B8A6")
TEXT = colors.HexColor("#F5F7FA")
MUTED = colors.HexColor("#9CA3AF")
BORDER = colors.HexColor("#1F2A33")
NAVY = CYAN  # section accents
ACCENT = CYAN
LIGHT = CARD
GRAY = MUTED

FONT_DIR = Path(__file__).resolve().parent / "fonts"
FONT_REG = "DejaVu"
FONT_BOLD = "DejaVu-Bold"


def _register_fonts() -> None:
    """Embed DejaVu so Indian Rupee (₹) and Unicode text render in PDF."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    registered = set(pdfmetrics.getRegisteredFontNames())
    regular = FONT_DIR / "DejaVuSans.ttf"
    bold = FONT_DIR / "DejaVuSans-Bold.ttf"
    if not regular.exists() or not bold.exists():
        raise FileNotFoundError(
            f"DejaVu fonts missing under {FONT_DIR}. Required for ₹ rendering."
        )
    if FONT_REG not in registered:
        pdfmetrics.registerFont(TTFont(FONT_REG, str(regular)))
    if FONT_BOLD not in registered:
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))
    # Map <b> tags inside Paragraphs to DejaVu-Bold (not Helvetica-Bold)
    pdfmetrics.registerFontFamily(
        FONT_REG,
        normal=FONT_REG,
        bold=FONT_BOLD,
        italic=FONT_REG,
        boldItalic=FONT_BOLD,
    )


class PDFReportGenerator:
    def __init__(self, firm: dict[str, str]):
        _register_fonts()
        self.firm = firm
        self.styles = self._build_styles()

    def _build_styles(self):
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="CoverTitle",
                fontName=FONT_BOLD,
                fontSize=22,
                textColor=TEXT,
                alignment=TA_CENTER,
                spaceAfter=12,
            )
        )
        styles.add(
            ParagraphStyle(
                name="CoverSub",
                fontName=FONT_REG,
                fontSize=12,
                textColor=CYAN,
                alignment=TA_CENTER,
                spaceAfter=8,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SectionHead",
                fontName=FONT_BOLD,
                fontSize=14,
                textColor=CYAN,
                spaceBefore=16,
                spaceAfter=8,
                borderPadding=4,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SubHead",
                fontName=FONT_BOLD,
                fontSize=11,
                textColor=CYAN_DIM,
                spaceBefore=10,
                spaceAfter=6,
            )
        )
        styles.add(
            ParagraphStyle(
                name="BodyText2",
                fontName=FONT_REG,
                fontSize=9,
                textColor=MUTED,
                alignment=TA_JUSTIFY,
                spaceAfter=6,
                leading=13,
            )
        )
        styles.add(
            ParagraphStyle(
                name="FooterStyle",
                fontName=FONT_REG,
                fontSize=8,
                textColor=GRAY,
                alignment=TA_CENTER,
            )
        )
        styles.add(
            ParagraphStyle(
                name="BulletText",
                fontName=FONT_REG,
                fontSize=9,
                textColor=MUTED,
                leading=12,
                leftIndent=10,
            )
        )
        return styles

    def generate(
        self,
        plan: dict[str, Any],
        profile: ClientFinancialProfile,
        output_path: str | Path,
        chart_paths: list[str] | None = None,
    ) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        chart_paths = chart_paths or []
        charts = {Path(p).stem: p for p in chart_paths}

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
            title=f"Financial Plan — {profile.personal.full_name}",
            author=self.firm.get("name", ""),
        )

        story: list[Any] = []
        story.extend(self._cover_page(plan, profile))
        story.append(PageBreak())
        story.extend(self._toc())
        story.append(PageBreak())
        story.extend(self._executive_summary(plan, profile, charts))
        story.append(PageBreak())
        story.extend(self._financial_health(plan, charts))
        story.append(PageBreak())
        story.extend(self._risk_profile(plan))
        story.append(PageBreak())
        story.extend(self._cash_flow_networth(plan, charts))
        story.append(PageBreak())
        story.extend(self._goals_section(plan, charts))
        story.append(PageBreak())
        story.extend(self._retirement_section(plan, charts))
        story.append(PageBreak())
        story.extend(self._investments_section(plan, charts))
        story.append(PageBreak())
        story.extend(self._insurance_section(plan))
        story.append(PageBreak())
        story.extend(self._tax_section(plan))
        story.append(PageBreak())
        story.extend(self._loans_section(plan))
        story.append(PageBreak())
        story.extend(self._scenarios_section(plan, charts))
        story.append(PageBreak())
        story.extend(self._recommendations_section(plan))
        story.append(PageBreak())
        story.extend(self._action_plan(plan))
        story.append(PageBreak())
        story.extend(self._estate_section(plan))
        story.append(PageBreak())
        story.extend(self._appendix(plan, profile))

        def _footer(canvas, doc_):
            canvas.saveState()
            width, height = A4
            # Dark page background
            canvas.setFillColor(BG)
            canvas.rect(0, 0, width, height, fill=1, stroke=0)
            # Cyan top accent
            canvas.setStrokeColor(CYAN)
            canvas.setLineWidth(1.2)
            canvas.line(18 * mm, height - 10 * mm, width - 18 * mm, height - 10 * mm)
            # Footer
            canvas.setFont(FONT_REG, 8)
            canvas.setFillColor(MUTED)
            canvas.drawString(
                18 * mm,
                10 * mm,
                f"{self.firm.get('name', '')} | Confidential | {profile.personal.full_name}",
            )
            canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {doc_.page}")
            canvas.setStrokeColor(BORDER)
            canvas.setLineWidth(0.6)
            canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
            canvas.restoreState()

        doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
        return output_path

    def _table(self, data, col_widths=None):
        t = Table(data, colWidths=col_widths, hAlign="LEFT")
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
            ("TEXTCOLOR", (0, 0), (-1, 0), CYAN),
            ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 1), (-1, -1), FONT_REG),
            ("TEXTCOLOR", (0, 1), (-1, -1), TEXT),
            ("BACKGROUND", (0, 1), (-1, -1), CARD),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CARD, CARD_ALT]),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
        t.setStyle(TableStyle(style))
        return t

    def _kv_table(self, pairs):
        data = [["Metric", "Value"]] + [[k, str(v)] for k, v in pairs]
        return self._table(data, col_widths=[3.2 * inch, 3.2 * inch])

    def _maybe_image(self, charts: dict, key: str, width=5.8 * inch):
        path = charts.get(key)
        if path and Path(path).exists():
            return [Spacer(1, 8), Image(path, width=width, height=width * 0.55), Spacer(1, 8)]
        return []

    def _cover_page(self, plan, profile):
        s = self.styles
        story = [Spacer(1, 1.2 * inch)]
        story.append(Paragraph(self.firm.get("name", "WealthCraft Advisors"), s["CoverTitle"]))
        story.append(Paragraph(self.firm.get("tagline", ""), s["CoverSub"]))
        story.append(Spacer(1, 0.4 * inch))
        story.append(Paragraph("COMPREHENSIVE FINANCIAL PLAN", s["CoverTitle"]))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(f"<b>Prepared for</b><br/>{profile.personal.full_name or 'Client'}", s["CoverSub"]))
        story.append(Paragraph(f"Age {profile.personal.age} | Retirement Age {profile.personal.retirement_age}", s["CoverSub"]))
        story.append(Paragraph(f"Risk Profile: {plan['summary'].get('risk_profile', '').title()}", s["CoverSub"]))
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(datetime.now().strftime("%d %B %Y"), s["CoverSub"]))
        story.append(Spacer(1, 0.8 * inch))
        story.append(
            Paragraph(
                f"Contact: {self.firm.get('email', '')} | {self.firm.get('phone', '')}",
                s["FooterStyle"],
            )
        )
        story.append(Spacer(1, 0.3 * inch))
        story.append(
            Paragraph(
                "Confidential. Projections are illustrative and based on configurable assumptions. "
                "Past performance does not guarantee future results. Seek advice from a SEBI-registered advisor.",
                s["BodyText2"],
            )
        )
        return story

    def _toc(self):
        s = self.styles
        items = [
            "1. Executive Summary",
            "2. Financial Health Scorecard",
            "3. Risk Profile Assessment",
            "4. Cash Flow & Net Worth",
            "5. Goal Planning",
            "6. Retirement Planning",
            "7. Investment Portfolio & Asset Allocation",
            "8. Insurance Analysis",
            "9. Tax Planning",
            "10. Loan Analysis",
            "11. Scenario Analysis",
            "12. Recommendations",
            "13. Action Plan",
            "14. Estate Planning Checklist",
            "15. Appendix — Assumptions & Methodology",
        ]
        story = [Paragraph("Table of Contents", s["SectionHead"]), Spacer(1, 8)]
        for item in items:
            story.append(Paragraph(item, s["BodyText2"]))
        return story

    def _executive_summary(self, plan, profile, charts):
        s = self.styles
        summary = plan["summary"]
        story = [Paragraph("1. Executive Summary", s["SectionHead"])]
        story.append(
            Paragraph(
                f"This comprehensive financial plan for <b>{profile.personal.full_name or 'the client'}</b> "
                f"evaluates net worth, cash flows, goals, retirement readiness, insurance adequacy, "
                f"tax efficiency, and investment allocation. The overall Financial Health Score is "
                f"<b>{summary['health_score']}/100 (Grade {summary['health_grade']})</b>.",
                s["BodyText2"],
            )
        )
        story.append(self._kv_table([
            ("Net Worth", format_inr(summary["net_worth"])),
            ("Monthly Income", format_inr(summary["monthly_income"])),
            ("Monthly Surplus", format_inr(summary["monthly_surplus"])),
            ("Retirement Progress", f"{summary['retirement_progress_percent']}%"),
            ("Recommended Tax Regime", summary["recommended_tax_regime"].upper()),
            ("FIRE Number", format_inr(plan["fire"]["fire_number"])),
            ("Goals Tracked", summary["total_goals"]),
            ("Active Loans", summary["total_loans"]),
        ]))
        story.extend(self._maybe_image(charts, "net_worth"))
        story.append(Paragraph("Key Highlights", s["SubHead"]))
        highlights = plan["recommendations"].get("priority_actions", [])[:5]
        if highlights:
            bullets = [
                ListItem(Paragraph(f"<b>{a['area']}:</b> {a['action']}", s["BulletText"]))
                for a in highlights
            ]
            story.append(ListFlowable(bullets, bulletType="bullet"))
        return story

    def _financial_health(self, plan, charts):
        s = self.styles
        hs = plan["health_score"]
        story = [Paragraph("2. Financial Health Scorecard", s["SectionHead"])]
        story.append(
            Paragraph(
                f"Composite score: <b>{hs['score']}/100 — Grade {hs['grade']}</b>. {hs['interpretation']}",
                s["BodyText2"],
            )
        )
        rows = [["Component", "Score (0-100)", "Weight"]]
        weights = hs.get("weights", {})
        for k, v in hs.get("component_scores", {}).items():
            rows.append([k.replace("_", " ").title(), f"{v}", str(weights.get(k, ""))])
        story.append(self._table(rows))
        story.extend(self._maybe_image(charts, "health_score"))
        story.append(Paragraph("Priority Improvements", s["SubHead"]))
        for tip in hs.get("top_improvements", []):
            story.append(Paragraph(f"• {tip}", s["BodyText2"]))
        return story

    def _risk_profile(self, plan):
        s = self.styles
        risk = plan["risk"]
        story = [Paragraph("3. Risk Profile Assessment", s["SectionHead"])]
        story.append(
            Paragraph(
                f"Investment personality: <b>{risk.get('personality', '')}</b> "
                f"({str(risk.get('profile', '')).title()}). {risk.get('description', '')}",
                s["BodyText2"],
            )
        )
        if risk.get("total_score") is not None:
            story.append(
                Paragraph(
                    f"Questionnaire score: {risk['total_score']} / {risk.get('max_score', 40)}",
                    s["BodyText2"],
                )
            )
        target = plan["portfolio"]["target"].get("target_allocation", {})
        if target:
            rows = [["Asset Class", "Target Allocation"]]
            for k, v in target.items():
                pct = v * 100 if v <= 1 else v
                rows.append([k.replace("_", " ").title(), f"{pct:.1f}%"])
            story.append(Paragraph("Suggested Asset Allocation", s["SubHead"]))
            story.append(self._table(rows))
        return story

    def _cash_flow_networth(self, plan, charts):
        s = self.styles
        story = [Paragraph("4. Cash Flow & Net Worth", s["SectionHead"])]
        nw = plan["net_worth"]
        cf = plan["cash_flow"]
        ratios = plan["ratios"]
        story.append(Paragraph("Net Worth", s["SubHead"]))
        story.append(self._kv_table([
            ("Total Assets", format_inr(nw["total_assets"])),
            ("Financial Assets", format_inr(nw["financial_assets"])),
            ("Real Estate", format_inr(nw["real_estate"])),
            ("Total Liabilities", format_inr(nw["total_liabilities"])),
            ("Net Worth", format_inr(nw["net_worth"])),
        ]))
        story.extend(self._maybe_image(charts, "cash_flow"))
        story.append(Paragraph("Monthly Cash Flow", s["SubHead"]))
        story.append(self._kv_table([
            ("Income", format_inr(cf["monthly_income"])),
            ("Expenses", format_inr(cf["monthly_expenses"])),
            ("EMI", format_inr(cf["monthly_emi"])),
            ("SIP", format_inr(cf["monthly_sip"])),
            ("Surplus", format_inr(cf["monthly_surplus"])),
            ("Savings Ratio", f"{ratios['savings_ratio_percent']}%"),
            ("Debt-to-Income", f"{ratios['debt_to_income_percent']}%"),
        ]))
        ef = plan["emergency_fund"]
        story.append(Paragraph("Emergency Fund", s["SubHead"]))
        story.append(
            Paragraph(
                f"Coverage: {ef['coverage_months']} months vs recommended {ef['recommended_months']}. "
                f"{ef['recommendation']}",
                s["BodyText2"],
            )
        )
        story.extend(self._maybe_image(charts, "expense_breakdown"))
        return story

    def _goals_section(self, plan, charts):
        s = self.styles
        story = [Paragraph("5. Goal Planning", s["SectionHead"])]
        story.append(
            Paragraph(
                "Each goal is inflation-adjusted to future cost. Required SIP and lumpsum amounts "
                "use the client's risk-aligned expected return.",
                s["BodyText2"],
            )
        )
        goals = plan.get("goals", [])
        if not goals:
            story.append(Paragraph("No goals configured for this client.", s["BodyText2"]))
            return story
        rows = [["Goal", "Future Cost", "Years", "Monthly SIP", "Progress"]]
        for g in goals:
            rows.append([
                g["name"][:24],
                format_inr(g["future_cost"]),
                str(g["years_to_goal"]),
                format_inr(g["monthly_sip_required"]),
                f"{g['progress_percent']}%",
            ])
        story.append(self._table(rows))
        story.extend(self._maybe_image(charts, "goal_progress"))
        for g in goals:
            story.append(Paragraph(g["name"], s["SubHead"]))
            story.append(
                Paragraph(
                    f"Type: {g['goal_type'].replace('_', ' ').title()} | Priority: {g['priority'].title()} | "
                    f"Current cost {format_inr(g['current_cost'])} grows to {format_inr(g['future_cost'])} "
                    f"in {g['years_to_goal']} years at {g['inflation_rate']*100:.1f}% inflation. "
                    f"Required monthly SIP: {format_inr(g['monthly_sip_required'])}. "
                    f"Funding gap: {format_inr(g['funding_gap'])}.",
                    s["BodyText2"],
                )
            )
        return story

    def _retirement_section(self, plan, charts):
        s = self.styles
        ret = plan["retirement"]
        story = [Paragraph("6. Retirement Planning", s["SectionHead"])]
        story.append(
            Paragraph(
                f"Retirement in <b>{ret['years_to_retirement']} years</b> at age {ret['retirement_age']}, "
                f"with a planning horizon of {ret['years_in_retirement']} years in retirement. "
                f"Required corpus: <b>{format_inr(ret['required_corpus'])}</b>. "
                f"Projected corpus: <b>{format_inr(ret['projected_corpus'])}</b>.",
                s["BodyText2"],
            )
        )
        story.append(self._kv_table([
            ("Annual Need at Retirement", format_inr(ret["total_annual_need_at_retirement"])),
            ("Monthly Income Needed", format_inr(ret["monthly_retirement_income_needed"])),
            ("Passive Income", format_inr(ret["passive_income_at_retirement"])),
            ("Shortfall", format_inr(ret["shortfall"])),
            ("Additional Monthly SIP", format_inr(ret["additional_monthly_sip_required"])),
            ("Progress", f"{ret['progress_percent']}%"),
            ("Sustainability (years)", ret["corpus_sustainability_years"]),
            ("Safe Withdrawal Rate", f"{ret['safe_withdrawal_rate']*100:.1f}%"),
        ]))
        story.extend(self._maybe_image(charts, "retirement"))
        story.append(Paragraph("Bucket Strategy", s["SubHead"]))
        for name, bucket in ret.get("bucket_strategy", {}).items():
            story.append(
                Paragraph(
                    f"<b>{name.replace('_', ' ').title()}</b> — {format_inr(bucket['amount'])} "
                    f"({bucket['allocation_percent']}%): {bucket['purpose']}. "
                    f"Instruments: {', '.join(bucket['instruments'])}.",
                    s["BodyText2"],
                )
            )
        mc = ret.get("monte_carlo", {})
        if mc:
            story.append(Paragraph("Monte Carlo Simulation", s["SubHead"]))
            story.append(Paragraph(mc.get("interpretation", ""), s["BodyText2"]))
            story.append(self._kv_table([
                ("Simulations", mc.get("simulations")),
                ("Success Rate", f"{mc.get('success_rate_percent')}%"),
                ("Median Ending Corpus", format_inr(mc.get("median_ending_corpus", 0))),
                ("10th Percentile", format_inr(mc.get("percentile_10", 0))),
                ("90th Percentile", format_inr(mc.get("percentile_90", 0))),
            ]))
        story.append(Paragraph("FIRE Analysis", s["SubHead"]))
        fire = plan["fire"]
        story.append(
            Paragraph(
                f"FIRE number at {fire['safe_withdrawal_rate']*100:.1f}% SWR: "
                f"{format_inr(fire['fire_number'])}. Current progress: {fire['current_progress_percent']}%.",
                s["BodyText2"],
            )
        )
        return story

    def _investments_section(self, plan, charts):
        s = self.styles
        story = [Paragraph("7. Investment Portfolio & Asset Allocation", s["SectionHead"])]
        story.extend(self._maybe_image(charts, "asset_allocation"))
        current = plan["portfolio"]["current"]
        rows = [["Asset Class", "Amount", "%"]]
        for k, v in current.get("asset_class", {}).items():
            rows.append([
                k.replace("_", " ").title(),
                format_inr(v),
                f"{current.get('asset_class_percent', {}).get(k, 0)}%",
            ])
        story.append(self._table(rows))
        story.append(Paragraph("Category Recommendations", s["SubHead"]))
        story.append(
            Paragraph(
                plan["recommendations"]["investment"].get("disclaimer", ""),
                s["BodyText2"],
            )
        )
        reco_rows = [["Category", "Allocation %", "Monthly Amount"]]
        for r in plan["recommendations"]["investment"].get("recommendations", []):
            reco_rows.append([r["name"], f"{r['allocation_percent']}%", format_inr(r["monthly_amount"])])
        if len(reco_rows) > 1:
            story.append(self._table(reco_rows))
        if plan["portfolio"].get("rebalancing"):
            story.append(Paragraph("Rebalancing Needs", s["SubHead"]))
            for item in plan["portfolio"]["rebalancing"]:
                story.append(
                    Paragraph(
                        f"• {item['asset_class'].title()}: {item['action']} by "
                        f"{abs(item['difference_percent'])}% "
                        f"(current {item['current_percent']}% → target {item['target_percent']}%)",
                        s["BodyText2"],
                    )
                )
        return story

    def _insurance_section(self, plan):
        s = self.styles
        ins = plan["insurance"]
        story = [Paragraph("8. Insurance Analysis", s["SectionHead"])]
        story.append(
            Paragraph(
                f"Human Life Value estimated at {format_inr(ins['human_life_value'])}. "
                f"Income replacement need: {format_inr(ins['income_replacement_need'])}.",
                s["BodyText2"],
            )
        )
        rows = [["Cover", "Existing", "Recommended", "Gap", "Status"]]
        for key in ("life", "health", "critical_illness", "accident"):
            d = ins[key]
            rows.append([
                key.replace("_", " ").title(),
                format_inr(d["existing_cover"]),
                format_inr(d["recommended_cover"]),
                format_inr(d["gap"]),
                "Adequate" if d["adequate"] else "Gap",
            ])
        story.append(self._table(rows))
        for rec in ins.get("recommendations", []):
            story.append(Paragraph(f"• {rec}", s["BodyText2"]))
        return story

    def _tax_section(self, plan):
        s = self.styles
        tax = plan["tax"]
        story = [Paragraph("9. Tax Planning", s["SectionHead"])]
        story.append(Paragraph(tax.get("recommendation_text", ""), s["BodyText2"]))
        old, new = tax["old_regime"], tax["new_regime"]
        rows = [
            ["Metric", "Old Regime", "New Regime"],
            ["Gross Income", format_inr(old["gross_income"]), format_inr(new["gross_income"])],
            ["Total Deductions", format_inr(old["total_deductions"]), format_inr(new["total_deductions"])],
            ["Taxable Income", format_inr(old["taxable_income"]), format_inr(new["taxable_income"])],
            ["Total Tax", format_inr(old["total_tax"]), format_inr(new["total_tax"])],
            [
                "Effective Rate",
                f"{old['effective_tax_rate']*100:.2f}%",
                f"{new['effective_tax_rate']*100:.2f}%",
            ],
        ]
        story.append(self._table(rows))
        story.append(Paragraph("Old Regime Deduction Breakdown", s["SubHead"]))
        story.append(self._kv_table([
            ("Section 80C", format_inr(old.get("section_80c", 0))),
            ("Section 80CCD(1B)", format_inr(old.get("section_80ccd_1b", 0))),
            ("Section 80D", format_inr(old.get("section_80d", 0))),
            ("HRA Exemption", format_inr(old.get("hra_exemption", 0))),
            ("Home Loan Interest", format_inr(old.get("home_loan_interest_deduction", 0))),
        ]))
        return story

    def _loans_section(self, plan):
        s = self.styles
        story = [Paragraph("10. Loan Analysis", s["SectionHead"])]
        loans = plan.get("loans", [])
        if not loans:
            story.append(Paragraph("No loans configured.", s["BodyText2"]))
            return story
        rows = [["Loan", "Outstanding", "EMI", "Rate", "Interest Saved (prep)"]]
        for loan in loans:
            rows.append([
                loan["name"][:20],
                format_inr(loan["principal_outstanding"]),
                format_inr(loan["emi"]),
                f"{loan['interest_rate_annual']*100:.2f}%",
                format_inr(loan["interest_saved"]),
            ])
        story.append(self._table(rows))
        for loan in loans:
            story.append(Paragraph(loan["name"], s["SubHead"]))
            story.append(
                Paragraph(
                    f"Outstanding {format_inr(loan['principal_outstanding'])} at "
                    f"{loan['interest_rate_annual']*100:.2f}% for {loan['tenure_months_remaining']} months. "
                    f"Total interest without prepayment: {format_inr(loan['total_interest_without_prepayment'])}. "
                    f"Prepayment of {format_inr(loan['prepayment_amount'])} saves "
                    f"{format_inr(loan['interest_saved'])} and {loan['months_saved']} months.",
                    s["BodyText2"],
                )
            )
        return story

    def _scenarios_section(self, plan, charts):
        s = self.styles
        story = [Paragraph("11. Scenario Analysis", s["SectionHead"])]
        story.append(
            Paragraph(
                "Best, expected, and worst cases adjust salary growth, inflation, and return assumptions "
                "per the configurable scenario matrix.",
                s["BodyText2"],
            )
        )
        rows = [["Scenario", "Surplus/mo", "Required Corpus", "Projected", "Shortfall"]]
        for key, data in plan.get("scenarios", {}).items():
            rows.append([
                data.get("label", key),
                format_inr(data.get("monthly_surplus", 0)),
                format_inr(data.get("required_corpus", 0)),
                format_inr(data.get("projected_corpus", 0)),
                format_inr(data.get("shortfall", 0)),
            ])
        story.append(self._table(rows))
        story.extend(self._maybe_image(charts, "scenarios"))
        return story

    def _recommendations_section(self, plan):
        s = self.styles
        story = [Paragraph("12. Recommendations", s["SectionHead"])]
        for action in plan["recommendations"].get("priority_actions", []):
            story.append(
                Paragraph(
                    f"<b>P{action['priority']} — {action['area']}:</b> {action['action']}",
                    s["BodyText2"],
                )
            )
        story.append(Paragraph("Investment Categories (configurable, no scheme hardcoding)", s["SubHead"]))
        for r in plan["recommendations"]["investment"].get("recommendations", []):
            story.append(
                Paragraph(
                    f"• <b>{r['name']}</b> ({r['allocation_percent']}%) — "
                    f"{format_inr(r['monthly_amount'])}/month. {r['description']}",
                    s["BodyText2"],
                )
            )
        return story

    def _action_plan(self, plan):
        s = self.styles
        story = [Paragraph("13. 90-Day Action Plan", s["SectionHead"])]
        phases = [
            (
                "Days 1–30: Protection & Liquidity",
                [
                    "Close critical insurance gaps (term life and health).",
                    "Fund emergency reserve to the recommended number of months.",
                    "Review and update nominees on all financial accounts.",
                ],
            ),
            (
                "Days 31–60: Cash Flow & Debt",
                [
                    "Automate SIPs aligned to high-priority goals.",
                    "Evaluate prepayment of highest-interest loans.",
                    "Confirm optimal tax regime before investment locks for the year.",
                ],
            ),
            (
                "Days 61–90: Growth & Structure",
                [
                    "Rebalance portfolio toward target asset allocation.",
                    "Increase retirement contributions to close corpus shortfall.",
                    "Execute estate checklist items (Will, POA, guardian nomination).",
                ],
            ),
        ]
        # Merge engine priority actions into phase notes
        for title, bullets in phases:
            story.append(Paragraph(title, s["SubHead"]))
            for b in bullets:
                story.append(Paragraph(f"• {b}", s["BodyText2"]))
        return story

    def _estate_section(self, plan):
        s = self.styles
        story = [Paragraph("14. Estate Planning Checklist", s["SectionHead"])]
        rows = [["Item", "Priority", "Description"]]
        for item in plan.get("estate_checklist", []):
            rows.append([item["item"], item["priority"], item["description"][:80] + ("…" if len(item["description"]) > 80 else "")])
        if len(rows) > 1:
            story.append(self._table(rows, col_widths=[1.6 * inch, 0.9 * inch, 4 * inch]))
        return story

    def _appendix(self, plan, profile):
        s = self.styles
        story = [Paragraph("15. Appendix — Assumptions & Methodology", s["SectionHead"])]
        story.append(
            Paragraph(
                "All calculations use industry-standard formulas: compound growth, SIP future value "
                "(ordinary annuity), reducing-balance EMI amortization, Fisher real returns, "
                "growing-annuity present value for HLV and retirement, Safe Withdrawal Rate for FIRE, "
                "and Monte Carlo geometric Brownian motion for corpus sustainability.",
                s["BodyText2"],
            )
        )
        story.append(Paragraph("Assumptions Used in This Plan", s["SubHead"]))
        for section, data in plan.get("assumptions_used", {}).items():
            story.append(Paragraph(str(section).replace("_", " ").title(), s["SubHead"]))
            if isinstance(data, dict):
                pairs = []
                for k, v in data.items():
                    if isinstance(v, float) and v < 1:
                        pairs.append((k.replace("_", " ").title(), f"{v*100:.2f}%"))
                    else:
                        pairs.append((k.replace("_", " ").title(), v))
                story.append(self._kv_table(pairs))
            else:
                story.append(Paragraph(str(data), s["BodyText2"]))

        story.append(Paragraph("Disclaimer", s["SubHead"]))
        story.append(
            Paragraph(
                "This report is generated by the Professional Financial Planner system using client-provided "
                "inputs and configurable assumptions. It does not constitute personalized investment advice, "
                "a solicitation, or a guarantee of returns. Mutual fund and security investments are subject "
                "to market risks. Tax rules are applied based on the configured financial year and may change. "
                "Please verify with a SEBI-registered Investment Adviser and a qualified tax professional.",
                s["BodyText2"],
            )
        )
        story.append(Spacer(1, 20))
        story.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%d %B %Y %H:%M')} by "
                f"{self.firm.get('name', 'WealthCraft Advisors')}.",
                s["FooterStyle"],
            )
        )
        return story
