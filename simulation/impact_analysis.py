"""Financial and operational impact analysis for ForesightAI.

Quantifies the monetary, operational, and portfolio-level consequences
of predicted default events, providing actionable loss estimates and
risk-adjusted return calculations suitable for credit risk reporting.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class LoanProfile:
    """Complete financial profile of a single loan.

    Attributes:
        loan_id: Unique identifier.
        principal: Original loan amount.
        outstanding_balance: Current outstanding balance.
        interest_rate: Annual interest rate (decimal, e.g. 0.12 = 12%).
        remaining_tenure_months: Months remaining on the loan.
        collateral_value: Value of collateral (0 if unsecured).
        recovery_rate: Expected recovery fraction in case of default (0–1).
        probability_of_default: Model-estimated P(default).
    """

    loan_id: str
    principal: float
    outstanding_balance: float
    interest_rate: float
    remaining_tenure_months: int
    collateral_value: float = 0.0
    recovery_rate: float = 0.45
    probability_of_default: float = 0.05

    @property
    def loss_given_default(self) -> float:
        """LGD = max(0, EAD - Collateral Recovery) / EAD."""
        collateral_recovery = min(self.collateral_value * 0.80, self.outstanding_balance)
        net_loss = max(0.0, self.outstanding_balance - collateral_recovery)
        lgd = net_loss / self.outstanding_balance if self.outstanding_balance > 0 else self.recovery_rate
        return min(1.0, lgd)

    @property
    def expected_credit_loss(self) -> float:
        """ECL = PD × LGD × EAD (IFRS 9 simplified approach)."""
        return self.probability_of_default * self.loss_given_default * self.outstanding_balance

    @property
    def risk_adjusted_return(self) -> float:
        """Approximate risk-adjusted net interest income.

        RAR = (Interest Income) - ECL
        Interest Income ≈ balance × annual_rate × (tenure / 12)
        """
        interest_income = (
            self.outstanding_balance
            * self.interest_rate
            * (self.remaining_tenure_months / 12)
        )
        return interest_income - self.expected_credit_loss


class ImpactAnalyzer:
    """Quantifies financial impact of loan defaults at individual and portfolio level.

    Attributes:
        operational_cost_per_default: Average cost of default resolution
            (legal, recovery, staffing) in currency units.
        capital_charge_rate: Regulatory capital requirement as fraction
            of Risk-Weighted Assets (e.g. Basel III: ~8%).
    """

    def __init__(
        self,
        operational_cost_per_default: float = 5_000.0,
        capital_charge_rate: float = 0.08,
    ) -> None:
        """Initialise the ImpactAnalyzer.

        Args:
            operational_cost_per_default: Fixed cost of managing one default.
            capital_charge_rate: Capital charge as fraction of EAD (Basel III).
        """
        self.operational_cost_per_default = operational_cost_per_default
        self.capital_charge_rate = capital_charge_rate
        logger.info(
            "ImpactAnalyzer initialised: op_cost=%.2f, capital_rate=%.2f%%",
            operational_cost_per_default,
            capital_charge_rate * 100,
        )

    # ------------------------------------------------------------------
    # Single loan analysis
    # ------------------------------------------------------------------

    def analyse_loan(self, loan: LoanProfile) -> Dict[str, Any]:
        """Compute full impact analysis for one loan.

        Args:
            loan: LoanProfile with all financial parameters.

        Returns:
            Dict with ECL, LGD, capital charge, total cost, and RAR.
        """
        ecl = loan.expected_credit_loss
        lgd = loan.loss_given_default
        capital_charge = loan.outstanding_balance * self.capital_charge_rate
        operational_cost = self.operational_cost_per_default * loan.probability_of_default
        total_expected_cost = ecl + operational_cost
        rar = loan.risk_adjusted_return

        result = {
            "loan_id": loan.loan_id,
            "outstanding_balance": round(loan.outstanding_balance, 2),
            "probability_of_default": round(loan.probability_of_default, 4),
            "loss_given_default": round(lgd, 4),
            "expected_credit_loss": round(ecl, 2),
            "capital_charge": round(capital_charge, 2),
            "operational_cost": round(operational_cost, 2),
            "total_expected_cost": round(total_expected_cost, 2),
            "risk_adjusted_return": round(rar, 2),
            "net_value": round(rar - total_expected_cost, 2),
            "profitability_flag": "profitable" if rar > total_expected_cost else "loss-making",
        }
        logger.info(
            "Loan %s: ECL=%.2f, RAR=%.2f, Net=%.2f (%s)",
            loan.loan_id, ecl, rar,
            result["net_value"], result["profitability_flag"],
        )
        return result

    # ------------------------------------------------------------------
    # Portfolio analysis
    # ------------------------------------------------------------------

    def analyse_portfolio(self, loans: List[LoanProfile]) -> Dict[str, Any]:
        """Compute aggregate impact metrics for a loan portfolio.

        Args:
            loans: List of LoanProfile objects.

        Returns:
            Dict with portfolio-level ECL, capital requirement, RAR, and
            concentration risk metrics.

        Raises:
            ValueError: If loans list is empty.
        """
        if not loans:
            raise ValueError("Portfolio must contain at least one loan.")

        loan_analyses = [self.analyse_loan(loan) for loan in loans]

        total_balance      = sum(l.outstanding_balance for l in loans)
        total_ecl          = sum(a["expected_credit_loss"] for a in loan_analyses)
        total_capital      = sum(a["capital_charge"] for a in loan_analyses)
        total_op_cost      = sum(a["operational_cost"] for a in loan_analyses)
        total_rar          = sum(a["risk_adjusted_return"] for a in loan_analyses)
        total_net          = sum(a["net_value"] for a in loan_analyses)

        pd_values          = np.array([l.probability_of_default for l in loans])
        exposure_values    = np.array([l.outstanding_balance for l in loans])
        weighted_pd        = float(np.average(pd_values, weights=exposure_values))
        portfolio_ecl_rate = total_ecl / total_balance if total_balance > 0 else 0

        # Herfindahl-Hirschman Index for concentration risk
        market_shares = exposure_values / total_balance
        hhi = float(np.sum(market_shares ** 2))

        return {
            "n_loans": len(loans),
            "total_outstanding_balance": round(total_balance, 2),
            "total_expected_credit_loss": round(total_ecl, 2),
            "total_capital_required": round(total_capital, 2),
            "total_operational_cost": round(total_op_cost, 2),
            "total_risk_adjusted_return": round(total_rar, 2),
            "total_net_value": round(total_net, 2),
            "portfolio_ecl_rate_pct": round(portfolio_ecl_rate * 100, 4),
            "weighted_avg_pd": round(weighted_pd, 4),
            "hhi_concentration": round(hhi, 4),
            "concentration_risk": (
                "LOW" if hhi < 0.10 else "MEDIUM" if hhi < 0.25 else "HIGH"
            ),
            "profitable_loans": sum(1 for a in loan_analyses if a["profitability_flag"] == "profitable"),
            "loss_making_loans": sum(1 for a in loan_analyses if a["profitability_flag"] == "loss-making"),
            "loan_details": loan_analyses,
        }

    def sensitivity_analysis(
        self,
        loan: LoanProfile,
        pd_range: Optional[List[float]] = None,
        recovery_range: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """One-way sensitivity of ECL to PD and recovery rate.

        Args:
            loan: Base loan profile.
            pd_range: List of P(default) values to test (default: 0.01–0.50).
            recovery_range: List of recovery rate values (default: 0.20–0.70).

        Returns:
            Dict with pd_sensitivity and recovery_sensitivity tables.
        """
        pd_range = pd_range or [0.01, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
        recovery_range = recovery_range or [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]

        pd_table = []
        for pd_val in pd_range:
            test_loan = LoanProfile(
                loan_id=loan.loan_id, principal=loan.principal,
                outstanding_balance=loan.outstanding_balance,
                interest_rate=loan.interest_rate,
                remaining_tenure_months=loan.remaining_tenure_months,
                collateral_value=loan.collateral_value,
                recovery_rate=loan.recovery_rate,
                probability_of_default=pd_val,
            )
            pd_table.append({
                "pd": pd_val,
                "ecl": round(test_loan.expected_credit_loss, 2),
            })

        recovery_table = []
        for rr in recovery_range:
            test_loan = LoanProfile(
                loan_id=loan.loan_id, principal=loan.principal,
                outstanding_balance=loan.outstanding_balance,
                interest_rate=loan.interest_rate,
                remaining_tenure_months=loan.remaining_tenure_months,
                collateral_value=loan.collateral_value,
                recovery_rate=rr,
                probability_of_default=loan.probability_of_default,
            )
            recovery_table.append({
                "recovery_rate": rr,
                "ecl": round(test_loan.expected_credit_loss, 2),
            })

        return {
            "loan_id": loan.loan_id,
            "base_ecl": round(loan.expected_credit_loss, 2),
            "pd_sensitivity": pd_table,
            "recovery_sensitivity": recovery_table,
        }
