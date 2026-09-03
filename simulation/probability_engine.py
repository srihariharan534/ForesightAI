"""Bayesian probability engine for dynamic risk estimation.

Provides prior-to-posterior updating using Bayes' theorem, enabling
ForesightAI to refine risk estimates as new evidence (payments, delinquencies,
income changes) arrives throughout a loan's lifecycle.
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class EvidenceEvent:
    """A piece of evidence used to update the probability estimate.

    Attributes:
        event_type: Type of event (e.g. 'on_time_payment', 'missed_payment').
        likelihood_ratio: P(event | high_risk) / P(event | low_risk).
            > 1 = evidence of higher risk; < 1 = evidence of lower risk.
        weight: Importance weight for this evidence (default 1.0).
    """

    event_type: str
    likelihood_ratio: float
    weight: float = 1.0

    # Calibrated likelihood ratios for common events
    CALIBRATED: Dict[str, float] = field(default_factory=lambda: {
        "on_time_payment":    0.60,   # lowers risk estimate
        "early_payment":      0.45,   # strong signal of low risk
        "missed_payment":     3.50,   # significant risk increase
        "missed_2_payments":  8.00,
        "income_increase":    0.70,
        "income_decrease":    2.20,
        "new_credit_opened":  1.40,
        "credit_score_up_20": 0.75,
        "credit_score_dn_20": 1.80,
        "employment_change":  1.55,
        "loan_partial_prepay":0.55,
    })

    @classmethod
    def from_event_type(cls, event_type: str) -> "EvidenceEvent":
        """Create an EvidenceEvent with calibrated likelihood ratio.

        Args:
            event_type: One of the calibrated event type strings.

        Returns:
            EvidenceEvent with appropriate likelihood ratio.

        Raises:
            KeyError: If event_type is not in the calibrated table.
        """
        calibrated = {
            "on_time_payment":    0.60,
            "early_payment":      0.45,
            "missed_payment":     3.50,
            "missed_2_payments":  8.00,
            "income_increase":    0.70,
            "income_decrease":    2.20,
            "new_credit_opened":  1.40,
            "credit_score_up_20": 0.75,
            "credit_score_dn_20": 1.80,
            "employment_change":  1.55,
            "loan_partial_prepay":0.55,
        }
        if event_type not in calibrated:
            raise KeyError(
                f"Unknown event_type '{event_type}'. "
                f"Known: {sorted(calibrated.keys())}"
            )
        return cls(event_type=event_type, likelihood_ratio=calibrated[event_type])


class ProbabilityEngine:
    """Sequential Bayesian updater for loan default probability.

    Starts from a prior P(default) and updates it each time new evidence
    arrives, producing a posterior estimate suitable for real-time risk
    monitoring.

    Attributes:
        prior_pd: Initial P(default) before any evidence.
        posterior_pd: Current P(default) after all evidence applied.
        history: Ordered list of (event_type, posterior_after_update) tuples.
    """

    def __init__(self, prior_pd: float) -> None:
        """Initialise with a prior probability of default.

        Args:
            prior_pd: Prior P(default) in (0, 1).

        Raises:
            ValueError: If prior_pd is not in (0, 1).
        """
        if not 0 < prior_pd < 1:
            raise ValueError(
                f"prior_pd must be in (0, 1), got {prior_pd}. "
                "Use a small epsilon (e.g. 0.001) for extreme values."
            )
        self.prior_pd = prior_pd
        self.posterior_pd = prior_pd
        self.history: List[Tuple[str, float]] = [("prior", prior_pd)]
        logger.info("ProbabilityEngine initialised with prior_pd=%.4f.", prior_pd)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, evidence: EvidenceEvent) -> float:
        """Apply one Bayesian update step.

        Uses the odds-ratio form of Bayes' theorem for numerical stability:
            posterior_odds = prior_odds × likelihood_ratio^weight

        Args:
            evidence: EvidenceEvent containing likelihood_ratio and weight.

        Returns:
            Updated posterior P(default).
        """
        prior_odds = self.posterior_pd / (1.0 - self.posterior_pd)
        lr_weighted = evidence.likelihood_ratio ** evidence.weight
        posterior_odds = prior_odds * lr_weighted
        self.posterior_pd = float(np.clip(
            posterior_odds / (1.0 + posterior_odds), 1e-6, 1 - 1e-6
        ))
        self.history.append((evidence.event_type, self.posterior_pd))
        logger.debug(
            "Bayesian update: event='%s', LR=%.3f → posterior=%.4f",
            evidence.event_type, evidence.likelihood_ratio, self.posterior_pd,
        )
        return self.posterior_pd

    def update_many(self, events: List[str]) -> float:
        """Apply multiple sequential Bayesian updates from event type strings.

        Args:
            events: Ordered list of event type strings (calibrated).

        Returns:
            Final posterior P(default) after all updates.
        """
        for event_type in events:
            evidence = EvidenceEvent.from_event_type(event_type)
            self.update(evidence)
        return self.posterior_pd

    def reset(self) -> None:
        """Reset the posterior to the original prior."""
        self.posterior_pd = self.prior_pd
        self.history = [("prior", self.prior_pd)]
        logger.info("ProbabilityEngine reset to prior=%.4f.", self.prior_pd)

    def risk_trajectory(self) -> List[Dict[str, Any]]:
        """Return the full history of probability updates.

        Returns:
            List of dicts with 'step', 'event', 'probability_of_default'.
        """
        return [
            {"step": i, "event": event, "probability_of_default": round(pd, 6)}
            for i, (event, pd) in enumerate(self.history)
        ]

    def expected_loss(self, loan_amount: float, recovery_rate: float = 0.45) -> float:
        """Compute expected credit loss (ECL) using current posterior PD.

        ECL = PD × LGD × EAD
            where LGD = 1 - recovery_rate, EAD = loan_amount.

        Args:
            loan_amount: Exposure at default (loan amount).
            recovery_rate: Expected fraction recovered in default (default 45%).

        Returns:
            Expected credit loss in currency units.
        """
        lgd = 1.0 - recovery_rate
        ecl = self.posterior_pd * lgd * loan_amount
        logger.info(
            "ECL: PD=%.4f, LGD=%.2f, EAD=%.2f → ECL=%.2f",
            self.posterior_pd, lgd, loan_amount, ecl,
        )
        return ecl

    def calibration_score(
        self,
        actual_defaults: List[int],
        predicted_pds: List[float],
    ) -> Dict[str, float]:
        """Compute Brier score and log-loss for model calibration.

        Args:
            actual_defaults: Binary outcomes (1 = defaulted, 0 = not).
            predicted_pds: Predicted P(default) for each observation.

        Returns:
            Dict with 'brier_score' and 'log_loss'.

        Raises:
            ValueError: If lists have different lengths or are empty.
        """
        if len(actual_defaults) != len(predicted_pds) or not actual_defaults:
            raise ValueError("actual_defaults and predicted_pds must be non-empty and same length.")

        y = np.array(actual_defaults, dtype=float)
        p = np.clip(np.array(predicted_pds, dtype=float), 1e-9, 1 - 1e-9)

        brier = float(np.mean((p - y) ** 2))
        log_loss = float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))

        return {"brier_score": round(brier, 6), "log_loss": round(log_loss, 6)}

    def summary(self) -> Dict[str, Any]:
        """Return a JSON-serialisable summary of the current engine state.

        Returns:
            Dict with prior, posterior, shift, and trajectory length.
        """
        return {
            "prior_pd": round(self.prior_pd, 6),
            "posterior_pd": round(self.posterior_pd, 6),
            "absolute_shift": round(self.posterior_pd - self.prior_pd, 6),
            "n_updates": len(self.history) - 1,
        }
