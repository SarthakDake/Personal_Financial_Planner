"""Matplotlib chart generator for PDF/Excel embedding."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


class ChartGenerator:
    """Produces professional charts saved as PNG files."""

    COLORS = ["#0B3D5C", "#1F6F8B", "#99C24D", "#F18F01", "#C73E1D", "#3A506B", "#5BC0BE"]

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
        ax.set_title(title, fontsize=13, fontweight="bold", color="#0B3D5C", pad=12)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(colors="#334155")

    def _net_worth_chart(self, plan: dict, path: Path) -> Path:
        nw = plan["net_worth"]
        labels = ["Assets", "Liabilities", "Net Worth"]
        values = [nw["total_assets"], nw["total_liabilities"], nw["net_worth"]]
        colors = [self.COLORS[0], self.COLORS[4], self.COLORS[2]]
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
            )
        fig.tight_layout()
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    def _asset_allocation_chart(self, plan: dict, path: Path) -> Path:
        ac = plan["portfolio"]["current"].get("asset_class", {})
        labels = [k.replace("_", " ").title() for k, v in ac.items() if v > 0]
        sizes = [v for v in ac.values() if v > 0]
        if not sizes:
            return path
        fig, ax = plt.subplots(figsize=(6, 5))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=self.COLORS[: len(sizes)],
            startangle=90,
            pctdistance=0.75,
        )
        for t in autotexts:
            t.set_fontsize(8)
        ax.set_title("Asset Allocation", fontsize=13, fontweight="bold", color="#0B3D5C")
        fig.tight_layout()
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

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
        colors = [self.COLORS[0], self.COLORS[4], self.COLORS[3], self.COLORS[1], self.COLORS[2]]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(labels, values, color=colors, width=0.55)
        self._style(ax, "Monthly Cash Flow")
        ax.set_ylabel("₹ / month")
        fig.tight_layout()
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    def _goal_progress_chart(self, plan: dict, path: Path) -> Path:
        goals = plan.get("goals", [])
        if not goals:
            fig, ax = plt.subplots(figsize=(7, 3))
            ax.text(0.5, 0.5, "No goals configured", ha="center", va="center")
            ax.axis("off")
            fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            return path
        names = [g["name"][:20] for g in goals[:8]]
        progress = [g["progress_percent"] for g in goals[:8]]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(names, progress, color=self.COLORS[1])
        ax.set_xlim(0, 100)
        self._style(ax, "Goal Funding Progress (%)")
        fig.tight_layout()
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    def _retirement_chart(self, plan: dict, path: Path) -> Path:
        ret = plan["retirement"]
        labels = ["Required", "Projected", "Shortfall"]
        values = [
            ret["required_corpus"],
            ret["projected_corpus"],
            ret["shortfall"],
        ]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(labels, values, color=[self.COLORS[0], self.COLORS[2], self.COLORS[4]], width=0.5)
        self._style(ax, "Retirement Corpus Analysis")
        ax.set_ylabel("Amount (₹)")
        fig.tight_layout()
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    def _expense_chart(self, plan: dict, path: Path) -> Path:
        breakdown = plan["cash_flow"].get("expense_breakdown", {})
        labels = [k.replace("_", " ").title() for k, v in breakdown.items() if v > 0]
        sizes = [v for v in breakdown.values() if v > 0]
        if not sizes:
            return path
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=self.COLORS[: len(sizes)],
            startangle=90,
        )
        ax.set_title("Expense Breakdown", fontsize=13, fontweight="bold", color="#0B3D5C")
        fig.tight_layout()
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

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
        ax.set_xticklabels(names)
        ax.legend()
        self._style(ax, "Scenario Analysis — Retirement Corpus")
        fig.tight_layout()
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    def _health_score_chart(self, plan: dict, path: Path) -> Path:
        components = plan["health_score"].get("component_scores", {})
        if not components:
            return path
        labels = [k.replace("_", " ").title() for k in components]
        values = list(components.values())
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(labels, values, color=self.COLORS[1])
        ax.set_xlim(0, 100)
        self._style(ax, f"Financial Health Score: {plan['health_score'].get('score')} ({plan['health_score'].get('grade')})")
        fig.tight_layout()
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path
