# ForesightAI — Simulation Engine

The `simulation` package provides advanced risk analytics beyond point-estimate predictions. It quantifies uncertainty, stress-tests portfolios, and tracks the lifecycle of credit risk using Bayesian updates.

## Modules

### 1. Monte Carlo Engine (`monte_carlo.py`)
Runs thousands of stochastic simulations per loan to generate a probability distribution of default.
- Computes Value at Risk (VaR 95%, 99%) and Conditional VaR (Expected Shortfall).
- Supports antithetic variates for variance reduction.
- Customisable parameter distributions (e.g. normal for income, fixed for credit score).

### 2. Scenario Engine (`scenario_engine.py`)
Applies macroeconomic shocks to applicant features before running Monte Carlo simulations.
- **Built-in Scenarios**: Baseline, Income Drop 20%, Credit Score -50, Financial Crisis, Salary Increase 25%.
- Stress tests the model output to measure downside risk.

### 3. Risk Matrix (`risk_matrix.py`)
Translates continuous probability and exposure into an enterprise 5x5 risk rating.
- **Likelihood**: Rare, Unlikely, Possible, Likely, Almost Certain.
- **Impact**: Insignificant, Minor, Moderate, Major, Severe.
- Outputs discrete risk ratings: LOW, MEDIUM, HIGH, CRITICAL.

### 4. Probability Engine (`probability_engine.py`)
Bayesian updater for sequential risk tracking.
- Starts with the XGBoost prediction as a prior.
- Updates dynamically as evidence arrives (e.g., missed payments, changes in employment).
- Maintains a risk trajectory over the loan lifecycle.

### 5. Impact Analyzer (`impact_analysis.py`)
Computes financial metrics from the ML predictions.
- **Expected Credit Loss (ECL)**: Probability of Default × Loss Given Default × Exposure at Default.
- **Risk-Adjusted Return (RAR)**.
- Portfolio concentration metrics (Herfindahl-Hirschman Index).

## Usage Example

```python
from simulation.monte_carlo import MonteCarloEngine
from simulation.scenario_engine import ScenarioEngine

# 1. Run Baseline Monte Carlo
mc = MonteCarloEngine(n_simulations=5000)
result = mc.run(applicant_features)
print(f"95% VaR: {result.var_95:.2f}")

# 2. Run Stress Scenarios
scenarios = ScenarioEngine()
stress_test = scenarios.stress_test_summary(applicant_features)
print(f"Worst Case: {stress_test['worst_case']['scenario_name']}")
```
