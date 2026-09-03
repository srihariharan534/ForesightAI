"""Structured scenario engine for what-if analysis.

Provides a declarative, composable system for defining named scenarios,
applying parameter shocks, and comparing outcomes across scenario variants.
Integrates with the MonteCarloEngine for stochastic scenario evaluation.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from simulation.monte_carlo import MonteCarloEngine, SimulationResult

logger = logging.getLogger(__name__)


class ScenarioSeverity(str, Enum):
    """Severity classification for named scenarios."""
    BASE      = "base"
    OPTIMISTIC = "optimistic"
    ADVERSE   = "adverse"
    STRESSED  = "stressed"
    CRISIS    = "crisis"


@dataclass
class ParameterShock:
    """A single parameter perturbation applied in a scenario.

    Attributes:
        parameter: Name of the parameter to perturb.
        shock_type: One of 'absolute', 'relative', 'replace'.
        value: Shock magnitude (absolute change, relative multiplier, or new value).
    """

    parameter: str
    shock_type: str   # 'absolute' | 'relative' | 'replace'
    value: float

    def apply(self, base_value: float) -> float:
        """Apply this shock to a base parameter value.

        Args:
            base_value: Original parameter value.

        Returns:
            Shocked parameter value.

        Raises:
            ValueError: If shock_type is unrecognised.
        """
        if self.shock_type == "absolute":
            return base_value + self.value
        elif self.shock_type == "relative":
            return base_value * self.value
        elif self.shock_type == "replace":
            return self.value
        else:
            raise ValueError(f"Unknown shock_type '{self.shock_type}'.")


@dataclass
class Scenario:
    """Definition of a named what-if scenario.

    Attributes:
        name: Human-readable scenario name.
        description: Narrative description.
        severity: Severity classification.
        shocks: List of parameter shocks to apply.
        probability: Estimated real-world probability of this scenario (0–1).
        tags: Arbitrary tags for filtering/grouping.
    """

    name: str
    description: str
    severity: ScenarioSeverity = ScenarioSeverity.BASE
    shocks: List[ParameterShock] = field(default_factory=list)
    probability: float = 1.0
    tags: List[str] = field(default_factory=list)

    def apply(self, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all shocks to base_params and return the scenario params.

        Args:
            base_params: Original parameter dict.

        Returns:
            New parameter dict with shocks applied.
        """
        scenario_params = base_params.copy()
        for shock in self.shocks:
            if shock.parameter in scenario_params:
                original = float(scenario_params[shock.parameter])
                scenario_params[shock.parameter] = shock.apply(original)
                logger.debug(
                    "Shock applied — %s: %.2f → %.2f",
                    shock.parameter, original, scenario_params[shock.parameter],
                )
        return scenario_params


@dataclass
class ScenarioResult:
    """Result for a single evaluated scenario.

    Attributes:
        scenario: The scenario that was evaluated.
        sim_result: MonteCarloEngine output.
        base_result: Optional baseline SimulationResult for comparison.
        shocked_params: The parameter dict after shocks were applied.
    """

    scenario: Scenario
    sim_result: SimulationResult
    shocked_params: Dict[str, Any]
    base_result: Optional[SimulationResult] = None

    @property
    def delta_pd(self) -> Optional[float]:
        """Change in P(default) vs baseline, if baseline provided."""
        if self.base_result is None:
            return None
        return self.sim_result.probability_of_loss - self.base_result.probability_of_loss

    @property
    def pd_impact_pct(self) -> Optional[float]:
        """Percentage change in P(default) vs baseline."""
        if self.base_result is None or self.base_result.probability_of_loss == 0:
            return None
        return (self.delta_pd / self.base_result.probability_of_loss) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Serialise result to JSON-compatible dict."""
        out: Dict[str, Any] = {
            "scenario_name": self.scenario.name,
            "scenario_severity": self.scenario.severity.value,
            "scenario_probability": self.scenario.probability,
            "description": self.scenario.description,
            "shocked_params": self.shocked_params,
            **{f"sim_{k}": v for k, v in self.sim_result.summary().items()},
        }
        if self.delta_pd is not None:
            out["delta_pd"] = round(self.delta_pd, 6)
            out["pd_impact_pct"] = round(self.pd_impact_pct, 2) if self.pd_impact_pct else None
        return out


class ScenarioEngine:
    """Execute and compare multiple named scenarios against a baseline.

    Attributes:
        mc_engine: MonteCarloEngine used for stochastic evaluation.
        scenarios: Registry of named Scenario objects.
    """

    # ------------------------------------------------------------------
    # Pre-built scenario library
    # ------------------------------------------------------------------
    STANDARD_SCENARIOS: List[Scenario] = [
        Scenario(
            name="Baseline",
            description="No shocks applied; represents current state.",
            severity=ScenarioSeverity.BASE,
            probability=1.0,
            tags=["baseline"],
        ),
        Scenario(
            name="Income Drop 20%",
            description="Borrower income falls 20% due to job instability.",
            severity=ScenarioSeverity.ADVERSE,
            shocks=[ParameterShock("income", "relative", 0.80)],
            probability=0.15,
            tags=["income", "adverse"],
        ),
        Scenario(
            name="Credit Score Decline",
            description="Credit score drops 50 points (missed payments).",
            severity=ScenarioSeverity.ADVERSE,
            shocks=[ParameterShock("credit_score", "absolute", -50)],
            probability=0.12,
            tags=["credit", "adverse"],
        ),
        Scenario(
            name="Loan Amount +30%",
            description="Loan amount increases 30% (additional drawdown).",
            severity=ScenarioSeverity.STRESSED,
            shocks=[ParameterShock("loan_amount", "relative", 1.30)],
            probability=0.08,
            tags=["loan", "stressed"],
        ),
        Scenario(
            name="Job Loss",
            description="Borrower becomes unemployed; income drops 70%.",
            severity=ScenarioSeverity.STRESSED,
            shocks=[
                ParameterShock("income", "relative", 0.30),
                ParameterShock("years_employed", "replace", 0),
            ],
            probability=0.05,
            tags=["employment", "stressed"],
        ),
        Scenario(
            name="Financial Crisis",
            description="Macro shock: income −30%, credit score −80, prior default.",
            severity=ScenarioSeverity.CRISIS,
            shocks=[
                ParameterShock("income", "relative", 0.70),
                ParameterShock("credit_score", "absolute", -80),
                ParameterShock("has_previous_default", "replace", 1),
            ],
            probability=0.02,
            tags=["macro", "crisis"],
        ),
        Scenario(
            name="Improved Credit",
            description="Credit rehabilitation: score up 60 points.",
            severity=ScenarioSeverity.OPTIMISTIC,
            shocks=[ParameterShock("credit_score", "absolute", +60)],
            probability=0.10,
            tags=["credit", "optimistic"],
        ),
        Scenario(
            name="Salary Increase 25%",
            description="Promotion / wage growth improves repayment capacity.",
            severity=ScenarioSeverity.OPTIMISTIC,
            shocks=[ParameterShock("income", "relative", 1.25)],
            probability=0.20,
            tags=["income", "optimistic"],
        ),
    ]

    def __init__(
        self,
        n_simulations: int = 5_000,
        random_seed: int = 42,
    ) -> None:
        """Initialise the ScenarioEngine.

        Args:
            n_simulations: Monte Carlo trials per scenario.
            random_seed: Random seed for reproducibility.
        """
        self.mc_engine = MonteCarloEngine(
            n_simulations=n_simulations,
            random_seed=random_seed,
            use_antithetic=True,
        )
        self.scenarios: Dict[str, Scenario] = {
            s.name: s for s in self.STANDARD_SCENARIOS
        }
        logger.info("ScenarioEngine initialised with %d standard scenarios.", len(self.scenarios))

    def register_scenario(self, scenario: Scenario) -> None:
        """Register a custom scenario.

        Args:
            scenario: Scenario to add to the registry.
        """
        self.scenarios[scenario.name] = scenario
        logger.info("Custom scenario registered: '%s'.", scenario.name)

    def run_single(
        self,
        base_params: Dict[str, Any],
        scenario_name: str,
        baseline_result: Optional[SimulationResult] = None,
    ) -> ScenarioResult:
        """Run one named scenario.

        Args:
            base_params: Original loan feature dict.
            scenario_name: Name of the scenario to evaluate.
            baseline_result: Optional pre-computed baseline for delta calculation.

        Returns:
            ScenarioResult with simulation output and comparison metrics.

        Raises:
            KeyError: If scenario_name is not in the registry.
        """
        if scenario_name not in self.scenarios:
            raise KeyError(
                f"Scenario '{scenario_name}' not found. "
                f"Available: {list(self.scenarios.keys())}"
            )

        scenario = self.scenarios[scenario_name]
        shocked_params = scenario.apply(base_params)
        sim_result = self.mc_engine.run(params=shocked_params)

        return ScenarioResult(
            scenario=scenario,
            sim_result=sim_result,
            shocked_params=shocked_params,
            base_result=baseline_result,
        )

    def run_all(
        self,
        base_params: Dict[str, Any],
        scenario_names: Optional[List[str]] = None,
    ) -> Dict[str, ScenarioResult]:
        """Run all (or a subset of) registered scenarios.

        Args:
            base_params: Original loan feature dict.
            scenario_names: Subset of scenario names to run. Runs all if None.

        Returns:
            Dict mapping scenario name to ScenarioResult.
        """
        names = scenario_names or list(self.scenarios.keys())
        logger.info("Running %d scenarios for params: %s", len(names), base_params)

        # Compute baseline first
        baseline_result = self.mc_engine.run(params=base_params)
        results: Dict[str, ScenarioResult] = {}

        for name in names:
            try:
                results[name] = self.run_single(
                    base_params, name, baseline_result=baseline_result
                )
                logger.debug(
                    "Scenario '%s': P(default)=%.4f, delta=%.4f",
                    name,
                    results[name].sim_result.probability_of_loss,
                    results[name].delta_pd or 0,
                )
            except Exception as exc:
                logger.error("Scenario '%s' failed: %s", name, exc)

        return results

    def stress_test_summary(
        self,
        base_params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run all scenarios and produce a stress-test summary table.

        Args:
            base_params: Original loan feature dict.

        Returns:
            Dict with baseline P(default), all scenario P(defaults), and risk
            classification (green / amber / red) per scenario.
        """
        results = self.run_all(base_params)
        rows = []

        for name, res in results.items():
            pd_val = res.sim_result.probability_of_loss
            risk_color = "green" if pd_val < 0.10 else ("amber" if pd_val < 0.30 else "red")
            rows.append({
                "scenario": name,
                "severity": res.scenario.severity.value,
                "probability_of_default": round(pd_val, 4),
                "var_95": round(res.sim_result.var_95, 4),
                "delta_pd": round(res.delta_pd, 4) if res.delta_pd else 0,
                "risk_color": risk_color,
                "scenario_probability": res.scenario.probability,
            })

        rows.sort(key=lambda r: r["probability_of_default"], reverse=True)

        baseline = results.get("Baseline")
        return {
            "base_params": base_params,
            "baseline_pd": round(baseline.sim_result.probability_of_loss, 4) if baseline else None,
            "scenarios": rows,
            "worst_case": rows[0] if rows else None,
            "best_case": rows[-1] if rows else None,
        }
