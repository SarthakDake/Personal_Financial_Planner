"""Matplotlib chart generator for PDF/Excel embedding — dark neon theme."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

# Prefer DejaVu for ₹ in chart labels
_FONT_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "pdf_generator" / "fonts" / "DejaVuSans.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]
for _fp in _FONT_CANDIDATES:
    if _fp.exists():
        try:
            font_manager.fontManager.addfont(str(_fp))
            plt.rcParams["font.family"] = "DejaVu Sans"
        except Exception:
            pass
        break


class ChartGenerator:
    """Produces professional dark-theme charts saved as PNG files."""

    BG = "#0D0D0D"
    CARD = "#1A1A1A"
    TEXT = "#F5F7FA"
    MUTED = "#9CA3AF"
    CYAN = "#00D1FF"
    COLORS = ["#00D1FF", "#00A3FF", "#14B8A6", "#38BDF8", "#22D3EE", "#67E8F9", "#2DD4BF"]

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self, plan: dict[str, Any]) -> list[str]:
        paths: list[str] = []
        generators = [
            ("net_worth", self._net_worth_chart),
            ("asset_allocation", self._asset_allocation_chart),
            ("cash_flow", self._cash_flow_chart),
            ("goal_progress", self._goal_progress_chart),
            ("retirement", self._retirement_chart),
            ("expense_breakdown", self._expense_chart),
            ("scenarios", self._scenario_chart),
            ("health_score", self._health_score_chart),
        ]
        for name, fn in generators:
            try:
                path = fn(plan, self.output_dir / f"{name}.png")
                if path:
                    paths.append(str(path))
            except Exception:
                continue
        return paths

    def _style(self, ax, title: str) -> None:
        ax.set_facecolor(self.CARD)
        ax.set_title(title, fontsize=13, fontweight="bold", color=self.CYAN, pad=12)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(self.MUTED)
        ax.spines["bottom"].set_color(self.MUTED)
        ax.tick_params(colors=self.MUTED)
        ax.yaxis.label.set_color(self.MUTED)
        ax.xaxis.label.set_color(self.MUTED)

    def _save(self, fig, path: Path) -> Path:
        fig.patch.set_facecolor(self.BG)
        fig.tight_layout()
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=self.BG, edgecolor="none")
        plt.close(fig)
        return path

    def _net_worth_chart(self, plan: dict, path: Path) -> Path:
        nw = plan["net_worth"]
        labels = ["Assets", "Liabilities", "Net Worth"]
        values = [nw["total_assets"], nw["total_liabilities"], nw["net_worth"]]
        colors = [self.COLORS[0], "#FF5C7A", self.COLORS[2]]
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.bar(labels, values, color=colors, width=0.55)
        self._style(ax, "Net Worth Snapshot")
        ax.set_ylabel("Amount (₹)")
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"₹{val/1e5:.1f}L",
                ha="center",
                va="bottom",
                fontsize=9,
                color=self.TEXT,
            )
        return self._save(fig, path)

    def _asset_allocation_chart(self, plan: dict, path: Path) -> Path:
        ac = plan["portfolio"]["current"].get("asset_class", {})
        labels = [k.replace("_", " ").title() for k, v in ac.items() if v > 0]
        sizes = [v for v in ac.values() if v > 0]
        if not sizes:
            return path
        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor(self.BG)
        ax.set_facecolor(self.BG)
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=self.COLORS[: len(sizes)],
            startangle=90,
            pctdistance=0.75,
            wedgeprops={"linewidth": 1, "edgecolor": self.BG},
        )
        for t in texts:
            t.set_color(self.TEXT)
            t.set_fontsize(9)
        for t in autotexts:
            t.set_fontsize(8)
            t.set_color(self.BG)
        ax.set_title("Asset Allocation", fontsize=13, fontweight="bold", color=self.CYAN)
        return self._save(fig, path)

    def _cash_flow_chart(self, plan: dict, path: Path) -> Path:
        cf = plan["cash_flow"]
        labels = ["Income", "Expenses", "EMI", "SIP", "Surplus"]
        values = [
            cf["monthly_income"],
            cf["monthly_expenses"],
            cf["monthly_emi"],
            cf["monthly_sip"],
            cf["monthly_surplus"],
        ]
        colors = [self.COLORS[0], "#FF5C7A", "#FBBF24", self.COLORS[1], self.COLORS[2]]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(labels, values, color=colors, width=0.55)
        self._style(ax, "Monthly Cash Flow")
        ax.set_ylabel("₹ / month")
        return self._save(fig, path)

    def _goal_progress_chart(self, plan: dict, path: Path) -> Path:
        goals = plan.get("goals", [])
        if not goals:
            fig, ax = plt.subplots(figsize=(7, 3))
            ax.set_facecolor(self.CARD)
            ax.text(0.5, 0.5, "No goals configured", ha="center", va="center", color=self.MUTED)
            ax.axis("off")
            return self._save(fig, path)
        names = [g["name"][:20] for g in goals[:8]]
        progress = [g["progress_percent"] for g in goals[:8]]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(names, progress, color=self.CYAN)
        ax.set_xlim(0, 100)
        self._style(ax, "Goal Funding Progress (%)")
        return self._save(fig, path)

    def _retirement_chart(self, plan: dict, path: Path) -> Path:
        ret = plan["retirement"]
        labels = ["Required", "Projected", "Shortfall"]
        values = [
            ret["required_corpus"],
            ret["projected_corpus"],
            ret["shortfall"],
        ]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(labels, values, color=[self.COLORS[0], self.COLORS[2], "#FF5C7A"], width=0.5)
        self._style(ax, "Retirement Corpus Analysis")
        ax.set_ylabel("Amount (₹)")
        return self._save(fig, path)

    def _expense_chart(self, plan: dict, path: Path) -> Path:
        breakdown = plan["cash_flow"].get("expense_breakdown", {})
        labels = [k.replace("_", " ").title() for k, v in breakdown.items() if v > 0]
        sizes = [v for v in breakdown.values() if v > 0]
        if not sizes:
            return path
        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor(self.BG)
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=self.COLORS[: len(sizes)],
            startangle=90,
            wedgeprops={"linewidth": 1, "edgecolor": self.BG},
        )
        for t in texts:
            t.set_color(self.TEXT)
        for t in autotexts:
            t.set_color(self.BG)
            t.set_fontsize(8)
        ax.set_title("Expense Breakdown", fontsize=13, fontweight="bold", color=self.CYAN)
        return self._save(fig, path)

    def _scenario_chart(self, plan: dict, path: Path) -> Path:
        scenarios = plan.get("scenarios", {})
        if not scenarios:
            return path
        names = []
        projected = []
        required = []
        for key in ("best_case", "expected_case", "worst_case"):
            if key in scenarios:
                names.append(scenarios[key].get("label", key))
                projected.append(scenarios[key].get("projected_corpus", 0))
                required.append(scenarios[key].get("required_corpus", 0))
        x = range(len(names))
        fig, ax = plt.subplots(figsize=(7, 4))
        width = 0.35
        ax.bar([i - width / 2 for i in x], required, width, label="Required", color=self.COLORS[0])
        ax.bar([i + width / 2 for i in x], projected, width, label="Projected", color=self.COLORS[2])
        ax.set_xticks(list(x))
        ax.set_xticklabels(names, color=self.MUTED)
        leg = ax.legend(facecolor=self.CARD, edgecolor=self.MUTED)
        for text in leg.get_texts():
            text.set_color(self.TEXT)
        self._style(ax, "Scenario Analysis — Retirement Corpus")
        return self._save(fig, path)

    def _health_score_chart(self, plan: dict, path: Path) -> Path:
        components = plan["health_score"].get("component_scores", {})
        if not components:
            return path
        labels = [k.replace("_", " ").title() for k in components]
        values = list(components.values())
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(labels, values, color=self.CYAN)
        ax.set_xlim(0, 100)
        self._style(
            ax,
            f"Financial Health Score: {plan['health_score'].get('score')} ({plan['health_score'].get('grade')})",
        )
        return self._save(fig, path)
