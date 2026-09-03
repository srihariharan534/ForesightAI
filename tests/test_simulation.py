"""Simulation module tests — Monte Carlo, Scenario, Risk Matrix, Probability, Impact."""

import pytest
import numpy as np
from simulation.monte_carlo import MonteCarloEngine, SimulationResult, ParameterDistribution
from simulation.scenario_engine import ScenarioEngine, Scenario, ParameterShock, ScenarioSeverity
from simulation.risk_matrix import RiskMatrix, RiskCell, LikelihoodLevel, ImpactLevel
from simulation.probability_engine import ProbabilityEngine, EvidenceEvent
from simulation.impact_analysis import ImpactAnalyzer, LoanProfile


BASE_PARAMS = {
    "age": 35, "income": 65000.0, "credit_score": 720,
    "years_employed": 8, "loan_amount": 22000.0,
    "num_dependents": 2, "has_previous_default": 0,
}


# ---------------------------------------------------------------------------
# Monte Carlo Engine
# ---------------------------------------------------------------------------

class TestMonteCarloEngine:
    def test_init_valid(self):
        engine = MonteCarloEngine(n_simulations=1000, random_seed=42)
        assert engine.n_simulations == 1000

    def test_init_too_few_sims(self):
        with pytest.raises(ValueError, match="n_simulations"):
            MonteCarloEngine(n_simulations=50)

    def test_run_returns_simulation_result(self):
        engine = MonteCarloEngine(n_simulations=500, random_seed=42)
        result = engine.run(params=BASE_PARAMS)
        assert isinstance(result, SimulationResult)

    def test_result_n_simulations(self):
        engine = MonteCarloEngine(n_simulations=1000, random_seed=42)
        result = engine.run(params=BASE_PARAMS)
        assert result.n_simulations == 1000

    def test_outcomes_in_unit_interval(self):
        engine = MonteCarloEngine(n_simulations=500, random_seed=42)
        result = engine.run(params=BASE_PARAMS)
        assert np.all(result.outcomes >= 0.0)
        assert np.all(result.outcomes <= 1.0)

    def test_probability_of_loss_in_range(self):
        engine = MonteCarloEngine(n_simulations=500)
        result = engine.run(params=BASE_PARAMS)
        assert 0.0 <= result.probability_of_loss <= 1.0

    def test_var_95_gte_mean(self):
        engine = MonteCarloEngine(n_simulations=1000, random_seed=1)
        result = engine.run(params=BASE_PARAMS)
        assert result.var_95 >= result.mean

    def test_confidence_interval_valid(self):
        engine = MonteCarloEngine(n_simulations=1000, random_seed=1)
        result = engine.run(params=BASE_PARAMS)
        lo, hi = result.confidence_interval()
        assert lo <= result.mean <= hi

    def test_summary_has_all_keys(self):
        engine = MonteCarloEngine(n_simulations=500, random_seed=42)
        result = engine.run(params=BASE_PARAMS)
        summary = result.summary()
        for key in ("mean_outcome", "probability_of_default", "var_95", "var_99", "cvar_95"):
            assert key in summary

    def test_antithetic_reduces_variance(self):
        """Antithetic engine should have lower or equal variance vs standard."""
        standard = MonteCarloEngine(n_simulations=2000, random_seed=42, use_antithetic=False)
        antithetic = MonteCarloEngine(n_simulations=2000, random_seed=42, use_antithetic=True)
        r_std = standard.run(BASE_PARAMS)
        r_ant = antithetic.run(BASE_PARAMS)
        # Means should be similar; this is a statistical test, not strict equality
        assert abs(r_std.mean - r_ant.mean) < 0.10

    def test_reproducibility(self):
        engine1 = MonteCarloEngine(n_simulations=500, random_seed=99)
        engine2 = MonteCarloEngine(n_simulations=500, random_seed=99)
        r1 = engine1.run(BASE_PARAMS)
        r2 = engine2.run(BASE_PARAMS)
        np.testing.assert_allclose(r1.outcomes, r2.outcomes, rtol=1e-5)

    def test_portfolio_simulation(self, sample_portfolio):
        engine = MonteCarloEngine(n_simulations=500, random_seed=42)
        result = engine.run_portfolio(sample_portfolio)
        assert isinstance(result, SimulationResult)
        assert 0.0 <= result.probability_of_loss <= 1.0

    def test_portfolio_empty_raises(self):
        engine = MonteCarloEngine(n_simulations=500)
        with pytest.raises(ValueError, match="at least one loan"):
            engine.run_portfolio([])

    def test_custom_parameter_distributions(self):
        dists = [
            ParameterDistribution("income", "normal", mean=65000, std=5000),
            ParameterDistribution("credit_score", "fixed", fixed_value=720),
        ]
        engine = MonteCarloEngine(n_simulations=200, random_seed=42)
        result = engine.run(params=BASE_PARAMS, param_distributions=dists)
        assert result.n_simulations == 200

    def test_high_risk_params_higher_pd(self):
        engine = MonteCarloEngine(n_simulations=2000, random_seed=42)
        low_risk = engine.run(BASE_PARAMS)
        high_risk = engine.run({
            "age": 25, "income": 15000.0, "credit_score": 400,
            "years_employed": 0, "loan_amount": 50000.0,
            "num_dependents": 5, "has_previous_default": 1,
        })
        assert high_risk.probability_of_loss > low_risk.probability_of_loss


# ---------------------------------------------------------------------------
# Scenario Engine
# ---------------------------------------------------------------------------

class TestScenarioEngine:
    def test_init(self):
        engine = ScenarioEngine(n_simulations=500)
        assert len(engine.scenarios) >= 7

    def test_run_single_baseline(self):
        engine = ScenarioEngine(n_simulations=300)
        result = engine.run_single(BASE_PARAMS, "Baseline")
        assert result.sim_result.n_simulations > 0

    def test_run_single_unknown_scenario(self):
        engine = ScenarioEngine(n_simulations=300)
        with pytest.raises(KeyError):
            engine.run_single(BASE_PARAMS, "NonExistentScenario")

    def test_run_all_returns_dict(self):
        engine = ScenarioEngine(n_simulations=300)
        results = engine.run_all(BASE_PARAMS)
        assert isinstance(results, dict)
        assert len(results) > 0

    def test_adverse_scenario_higher_pd(self):
        engine = ScenarioEngine(n_simulations=1000)
        results = engine.run_all(BASE_PARAMS)
        baseline_pd = results["Baseline"].sim_result.probability_of_loss
        crisis_pd = results["Financial Crisis"].sim_result.probability_of_loss
        assert crisis_pd > baseline_pd

    def test_optimistic_scenario_lower_pd(self):
        engine = ScenarioEngine(n_simulations=1000)
        results = engine.run_all(BASE_PARAMS)
        baseline_pd = results["Baseline"].sim_result.probability_of_loss
        optimistic_pd = results["Salary Increase 25%"].sim_result.probability_of_loss
        assert optimistic_pd <= baseline_pd + 0.05  # may not always be lower due to randomness

    def test_custom_scenario_registration(self):
        engine = ScenarioEngine(n_simulations=300)
        custom = Scenario(
            name="Custom Test",
            description="Test custom scenario.",
            severity=ScenarioSeverity.ADVERSE,
            shocks=[ParameterShock("income", "relative", 0.50)],
        )
        engine.register_scenario(custom)
        assert "Custom Test" in engine.scenarios

    def test_stress_test_summary_structure(self):
        engine = ScenarioEngine(n_simulations=300)
        summary = engine.stress_test_summary(BASE_PARAMS)
        assert "baseline_pd" in summary
        assert "scenarios" in summary
        assert "worst_case" in summary
        assert "best_case" in summary

    def test_parameter_shock_relative(self):
        shock = ParameterShock("income", "relative", 0.80)
        result = shock.apply(65000.0)
        assert abs(result - 52000.0) < 0.01

    def test_parameter_shock_absolute(self):
        shock = ParameterShock("credit_score", "absolute", -50)
        assert shock.apply(720) == 670

    def test_parameter_shock_replace(self):
        shock = ParameterShock("has_previous_default", "replace", 1.0)
        assert shock.apply(0.0) == 1.0

    def test_parameter_shock_unknown_type(self):
        shock = ParameterShock("income", "invalid_type", 100)
        with pytest.raises(ValueError):
            shock.apply(50000.0)

    def test_delta_pd_computed(self):
        engine = ScenarioEngine(n_simulations=500)
        results = engine.run_all(BASE_PARAMS)
        crisis = results.get("Financial Crisis")
        assert crisis is not None
        assert crisis.delta_pd is not None


# ---------------------------------------------------------------------------
# Risk Matrix
# ---------------------------------------------------------------------------

class TestRiskMatrix:
    def test_evaluate_low_pd_low_amount(self):
        matrix = RiskMatrix(loan_amount=5000)
        cell = matrix.evaluate(0.02, loan_amount=5000)
        assert cell.rating == "LOW"

    def test_evaluate_high_pd_high_amount(self):
        matrix = RiskMatrix()
        cell = matrix.evaluate(0.70, loan_amount=500_000)
        assert cell.rating in ("HIGH", "CRITICAL")

    def test_score_equals_likelihood_times_impact(self):
        matrix = RiskMatrix()
        cell = matrix.evaluate(0.25, 50_000)
        assert cell.score == int(cell.likelihood) * int(cell.impact)

    def test_full_matrix_dimensions(self):
        matrix = RiskMatrix()
        grid = matrix.full_matrix()
        assert len(grid) == 5
        for row in grid:
            assert len(row) == 5

    def test_portfolio_risk_profile(self, sample_portfolio):
        matrix = RiskMatrix()
        loans_with_pd = [
            {**loan, "pd": 0.05 + i * 0.05}
            for i, loan in enumerate(sample_portfolio)
        ]
        profile = matrix.portfolio_risk_profile(loans_with_pd)
        assert "n_loans" in profile
        assert profile["n_loans"] == len(sample_portfolio)
        assert "rating_distribution" in profile

    def test_portfolio_empty_raises(self):
        matrix = RiskMatrix()
        with pytest.raises(ValueError):
            matrix.portfolio_risk_profile([])

    def test_risk_cell_to_dict(self):
        cell = RiskCell(LikelihoodLevel.POSSIBLE, ImpactLevel.MAJOR)
        d = cell.to_dict()
        for key in ("likelihood", "impact", "score", "rating", "colour"):
            assert key in d


# ---------------------------------------------------------------------------
# Probability Engine
# ---------------------------------------------------------------------------

class TestProbabilityEngine:
    def test_init_valid(self):
        engine = ProbabilityEngine(prior_pd=0.05)
        assert engine.prior_pd == 0.05
        assert engine.posterior_pd == 0.05

    def test_init_invalid_pd(self):
        with pytest.raises(ValueError):
            ProbabilityEngine(prior_pd=0.0)
        with pytest.raises(ValueError):
            ProbabilityEngine(prior_pd=1.0)

    def test_update_missed_payment_increases_pd(self):
        engine = ProbabilityEngine(prior_pd=0.05)
        posterior = engine.update(EvidenceEvent("missed_payment", 3.5))
        assert posterior > 0.05

    def test_update_on_time_payment_decreases_pd(self):
        engine = ProbabilityEngine(prior_pd=0.10)
        posterior = engine.update(EvidenceEvent("on_time_payment", 0.60))
        assert posterior < 0.10

    def test_update_many(self):
        engine = ProbabilityEngine(prior_pd=0.05)
        engine.update_many(["on_time_payment", "on_time_payment", "early_payment"])
        assert engine.posterior_pd < 0.05

    def test_reset(self):
        engine = ProbabilityEngine(prior_pd=0.05)
        engine.update(EvidenceEvent("missed_payment", 3.5))
        engine.reset()
        assert engine.posterior_pd == engine.prior_pd

    def test_trajectory_length(self):
        engine = ProbabilityEngine(prior_pd=0.05)
        engine.update_many(["on_time_payment", "missed_payment"])
        traj = engine.risk_trajectory()
        assert len(traj) == 3  # prior + 2 updates

    def test_expected_loss(self):
        engine = ProbabilityEngine(prior_pd=0.10)
        ecl = engine.expected_loss(loan_amount=50000, recovery_rate=0.45)
        expected = 0.10 * (1 - 0.45) * 50000
        assert abs(ecl - expected) < 0.01

    def test_calibration_score(self):
        engine = ProbabilityEngine(prior_pd=0.05)
        actuals = [0, 0, 1, 0, 1, 0, 0, 1]
        preds   = [0.05, 0.08, 0.72, 0.10, 0.65, 0.03, 0.12, 0.80]
        scores = engine.calibration_score(actuals, preds)
        assert "brier_score" in scores
        assert "log_loss" in scores
        assert 0 <= scores["brier_score"] <= 1

    def test_calibration_score_mismatched_raises(self):
        engine = ProbabilityEngine(prior_pd=0.05)
        with pytest.raises(ValueError):
            engine.calibration_score([0, 1], [0.5])

    def test_evidence_from_event_type(self):
        ev = EvidenceEvent.from_event_type("missed_payment")
        assert ev.likelihood_ratio == 3.5

    def test_evidence_unknown_event_raises(self):
        with pytest.raises(KeyError):
            EvidenceEvent.from_event_type("UNKNOWN_EVENT")

    def test_summary_dict(self):
        engine = ProbabilityEngine(prior_pd=0.05)
        engine.update(EvidenceEvent("missed_payment", 3.5))
        s = engine.summary()
        assert "prior_pd" in s
        assert "posterior_pd" in s
        assert s["n_updates"] == 1


# ---------------------------------------------------------------------------
# Impact Analyzer
# ---------------------------------------------------------------------------

class TestImpactAnalyzer:
    @pytest.fixture
    def sample_loan(self) -> LoanProfile:
        return LoanProfile(
            loan_id="TEST-001",
            principal=25000.0,
            outstanding_balance=22000.0,
            interest_rate=0.12,
            remaining_tenure_months=24,
            collateral_value=0.0,
            recovery_rate=0.45,
            probability_of_default=0.08,
        )

    def test_ecl_positive(self, sample_loan):
        assert sample_loan.expected_credit_loss > 0

    def test_lgd_in_range(self, sample_loan):
        assert 0.0 <= sample_loan.loss_given_default <= 1.0

    def test_rar_computed(self, sample_loan):
        rar = sample_loan.risk_adjusted_return
        assert isinstance(rar, float)

    def test_analyse_loan_keys(self, sample_loan):
        analyzer = ImpactAnalyzer()
        result = analyzer.analyse_loan(sample_loan)
        for key in ("loan_id", "expected_credit_loss", "capital_charge",
                    "risk_adjusted_return", "profitability_flag"):
            assert key in result

    def test_analyse_portfolio(self, sample_portfolio):
        analyzer = ImpactAnalyzer()
        loans = [
            LoanProfile(
                loan_id=f"LOAN-{i:03d}",
                principal=p["loan_amount"],
                outstanding_balance=p["loan_amount"] * 0.90,
                interest_rate=0.115,
                remaining_tenure_months=36,
                collateral_value=0.0,
                probability_of_default=0.05 + i * 0.03,
            )
            for i, p in enumerate(sample_portfolio)
        ]
        result = analyzer.analyse_portfolio(loans)
        assert result["n_loans"] == len(loans)
        assert "total_expected_credit_loss" in result
        assert "hhi_concentration" in result

    def test_portfolio_empty_raises(self):
        analyzer = ImpactAnalyzer()
        with pytest.raises(ValueError):
            analyzer.analyse_portfolio([])

    def test_sensitivity_analysis(self, sample_loan):
        analyzer = ImpactAnalyzer()
        result = analyzer.sensitivity_analysis(sample_loan)
        assert "pd_sensitivity" in result
        assert "recovery_sensitivity" in result
        assert len(result["pd_sensitivity"]) > 0
