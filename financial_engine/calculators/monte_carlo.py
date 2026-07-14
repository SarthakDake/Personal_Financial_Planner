"""Monte Carlo retirement simulation using geometric Brownian motion."""

from __future__ import annotations

from typing import Any

import numpy as np


class MonteCarloSimulator:
    """
    Simulates retirement portfolio outcomes.

    Model: annual returns ~ LogNormal(mu, sigma) with inflation-adjusted withdrawals.
    """

    def __init__(self, assumptions: dict[str, Any]):
        self.cfg = assumptions.get("retirement", {})

    def simulate_retirement(
        self,
        *,
        initial_corpus: float,
        annual_withdrawal: float,
        years: int,
        expected_return: float = 0.09,
        return_volatility: float = 0.15,
        inflation: float = 0.06,
        n_simulations: int | None = None,
        success_threshold: float | None = None,
        seed: int = 42,
    ) -> dict[str, Any]:
        n_simulations = n_simulations or int(self.cfg.get("monte_carlo_simulations", 1000))
        success_threshold = success_threshold or float(self.cfg.get("success_threshold", 0.85))

        if initial_corpus <= 0 or years <= 0:
            return {
                "simulations": n_simulations,
                "success_rate": 0.0,
                "median_ending_corpus": 0.0,
                "percentile_10": 0.0,
                "percentile_90": 0.0,
                "is_sustainable": False,
                "paths_sample": [],
            }

        rng = np.random.default_rng(seed)
        # Convert expected arithmetic return to log-return mean
        mu = np.log(1 + expected_return) - 0.5 * return_volatility**2
        sigma = return_volatility

        ending_values = np.zeros(n_simulations)
        success_count = 0
        sample_paths: list[list[float]] = []

        for i in range(n_simulations):
            balance = float(initial_corpus)
            withdrawal = float(annual_withdrawal)
            path = [balance]
            survived = True
            for _ in range(years):
                annual_return = float(np.exp(rng.normal(mu, sigma)) - 1)
                balance = balance * (1 + annual_return) - withdrawal
                withdrawal *= 1 + inflation
                if i < 20:
                    path.append(max(balance, 0.0))
                if balance <= 0:
                    balance = 0.0
                    survived = False
                    break
            ending_values[i] = balance
            if survived and balance > 0:
                success_count += 1
            if i < 20:
                sample_paths.append([round(v, 2) for v in path])

        success_rate = success_count / n_simulations

        return {
            "simulations": n_simulations,
            "horizon_years": years,
            "expected_return": expected_return,
            "volatility": return_volatility,
            "inflation": inflation,
            "initial_corpus": round(initial_corpus, 2),
            "initial_annual_withdrawal": round(annual_withdrawal, 2),
            "success_rate": round(success_rate, 4),
            "success_rate_percent": round(success_rate * 100, 2),
            "success_threshold": success_threshold,
            "is_sustainable": success_rate >= success_threshold,
            "median_ending_corpus": round(float(np.median(ending_values)), 2),
            "percentile_10": round(float(np.percentile(ending_values, 10)), 2),
            "percentile_25": round(float(np.percentile(ending_values, 25)), 2),
            "percentile_75": round(float(np.percentile(ending_values, 75)), 2),
            "percentile_90": round(float(np.percentile(ending_values, 90)), 2),
            "mean_ending_corpus": round(float(np.mean(ending_values)), 2),
            "paths_sample": sample_paths,
            "interpretation": (
                f"In {success_rate * 100:.1f}% of {n_simulations} simulations the corpus "
                f"sustained withdrawals for {years} years. "
                + (
                    "Plan appears sustainable."
                    if success_rate >= success_threshold
                    else "Consider increasing corpus, reducing withdrawal, or delaying retirement."
                )
            ),
        }
