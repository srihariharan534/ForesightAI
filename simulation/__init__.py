"""ForesightAI Simulation Engine.

This package provides a production-grade stochastic simulation framework
for risk modeling, scenario analysis, and Monte Carlo-based decision support.

Modules:
    monte_carlo: Monte Carlo simulation engine with variance reduction.
    scenario_engine: Structured scenario definition and execution.
    risk_matrix: Risk severity and likelihood matrix evaluation.
    probability_engine: Bayesian probability estimation and updating.
    impact_analysis: Financial and operational impact quantification.

Example::

    from simulation import MonteCarloEngine, ScenarioEngine, RiskMatrix

    engine = MonteCarloEngine(n_simulations=10_000, random_seed=42)
    results = engine.run(params={"loan_amount": 25000, "income": 55000})
    print(results.summary())
"""

from simulation.monte_carlo import MonteCarloEngine, SimulationResult
from simulation.scenario_engine import ScenarioEngine, Scenario
from simulation.risk_matrix import RiskMatrix, RiskCell
from simulation.probability_engine import ProbabilityEngine
from simulation.impact_analysis import ImpactAnalyzer

__all__ = [
    "MonteCarloEngine",
    "SimulationResult",
    "ScenarioEngine",
    "Scenario",
    "RiskMatrix",
    "RiskCell",
    "ProbabilityEngine",
    "ImpactAnalyzer",
]
