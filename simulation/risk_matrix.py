"""Risk matrix: severity × likelihood scoring for ForesightAI.

Implements a 5×5 risk matrix used to classify, score, and colour-code
risks by likelihood (probability) and impact (consequence severity),
producing actionable risk ratings for loan portfolios and applicants.
"""

import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LikelihoodLevel(IntEnum):
    """Likelihood (probability) rating on a 1–5 scale."""
    RARE        = 1   # < 5%
    UNLIKELY    = 2   # 5–15%
    POSSIBLE    = 3   # 15–35%
    LIKELY      = 4   # 35–65%
    ALMOST_CERTAIN = 5  # > 65%


class ImpactLevel(IntEnum):
    """Impact (consequence) rating on a 1–5 scale."""
    NEGLIGIBLE  = 1   # < ₹10K loss
    MINOR       = 2   # ₹10K–₹50K
    MODERATE    = 3   # ₹50K–₹2L
    MAJOR       = 4   # ₹2L–₹10L
    CATASTROPHIC = 5  # > ₹10L


# Colour-coded risk rating thresholds (score = likelihood × impact, max = 25)
_RATING_THRESHOLDS: List[Tuple[int, str, str]] = [
    (4,  "LOW",      "#22c55e"),   # green
    (9,  "MEDIUM",   "#eab308"),   # yellow
    (16, "HIGH",     "#f97316"),   # orange
    (25, "CRITICAL", "#ef4444"),   # red
]


def _score_to_rating(score: int) -> Tuple[str, str]:
    """Map a risk score (1–25) to a (rating_label, colour_hex) tuple.

    Args:
        score: Integer risk score (likelihood × impact).

    Returns:
        Tuple of (rating_str, hex_colour).
    """
    for threshold, label, colour in _RATING_THRESHOLDS:
        if score <= threshold:
            return label, colour
    return "CRITICAL", "#ef4444"


@dataclass
class RiskCell:
    """A single cell in the risk matrix.

    Attributes:
        likelihood: Likelihood level (1–5).
        impact: Impact level (1–5).
        score: Computed risk score (likelihood × impact).
        rating: Qualitative rating string (LOW / MEDIUM / HIGH / CRITICAL).
        colour: Hex colour code for visualisation.
        description: Human-readable cell description.
    """

    likelihood: LikelihoodLevel
    impact: ImpactLevel
    description: str = ""

    def __post_init__(self) -> None:
        self.score: int = int(self.likelihood) * int(self.impact)
        self.rating, self.colour = _score_to_rating(self.score)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise cell to JSON-safe dict."""
        return {
            "likelihood": self.likelihood.name,
            "likelihood_value": int(self.likelihood),
            "impact": self.impact.name,
            "impact_value": int(self.impact),
            "score": self.score,
            "rating": self.rating,
            "colour": self.colour,
            "description": self.description,
        }


class RiskMatrix:
    """5×5 risk matrix evaluator for ForesightAI loan risk assessment.

    Maps model-derived probabilities and financial exposure values into
    structured risk classifications suitable for regulatory reporting
    and dashboard visualisation.

    Attributes:
        loan_amount: Total loan exposure in currency units.
        cells: The full 5×5 matrix of RiskCell objects.
    """

    def __init__(self, loan_amount: float = 25_000.0) -> None:
        """Initialise the risk matrix.

        Args:
            loan_amount: Total loan amount (used for impact level calibration).
        """
        self.loan_amount = loan_amount
        self.cells = self._build_matrix()
        logger.info("RiskMatrix initialised for loan_amount=%.2f.", loan_amount)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        probability_of_default: float,
        loan_amount: Optional[float] = None,
    ) -> RiskCell:
        """Evaluate the risk cell for given PD and exposure.

        Args:
            probability_of_default: P(default) in [0, 1].
            loan_amount: Override loan amount for impact mapping. Uses
                         self.loan_amount if None.

        Returns:
            RiskCell at the intersection of likelihood and impact.
        """
        exposure = loan_amount or self.loan_amount
        likelihood = self._pd_to_likelihood(probability_of_default)
        impact = self._exposure_to_impact(exposure)

        cell = RiskCell(
            likelihood=likelihood,
            impact=impact,
            description=(
                f"P(default)={probability_of_default:.1%}, "
                f"Exposure=₹{exposure:,.0f}"
            ),
        )
        logger.info(
            "Risk evaluated: PD=%.4f, Impact=%s → Score=%d, Rating=%s",
            probability_of_default, impact.name, cell.score, cell.rating,
        )
        return cell

    def full_matrix(self) -> List[List[Dict[str, Any]]]:
        """Return the complete 5×5 matrix as a list-of-lists of cell dicts.

        Returns:
            5×5 grid where row index = impact (5→1 top-to-bottom),
            col index = likelihood (1→5 left-to-right).
        """
        grid = []
        for impact_val in range(5, 0, -1):
            row = []
            for likelihood_val in range(1, 6):
                cell = self.cells[likelihood_val][impact_val]
                row.append(cell.to_dict())
            grid.append(row)
        return grid

    def portfolio_risk_profile(
        self,
        loans: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Evaluate risk profile for a loan portfolio.

        Args:
            loans: List of dicts with keys 'pd' (probability_of_default)
                   and 'loan_amount'.

        Returns:
            Dict with rating distribution, weighted average risk score,
            and worst-case cell.
        """
        if not loans:
            raise ValueError("Portfolio must be non-empty.")

        cells = [
            self.evaluate(loan["pd"], loan.get("loan_amount", self.loan_amount))
            for loan in loans
        ]
        total_exposure = sum(loan.get("loan_amount", self.loan_amount) for loan in loans)

        # Weighted average score by exposure
        weighted_score = sum(
            cell.score * loan.get("loan_amount", self.loan_amount)
            for cell, loan in zip(cells, loans)
        ) / total_exposure

        rating_counts: Dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for cell in cells:
            rating_counts[cell.rating] += 1

        worst_cell = max(cells, key=lambda c: c.score)

        return {
            "n_loans": len(loans),
            "total_exposure": total_exposure,
            "weighted_avg_score": round(weighted_score, 2),
            "portfolio_rating": _score_to_rating(int(round(weighted_score)))[0],
            "rating_distribution": rating_counts,
            "worst_case": worst_cell.to_dict(),
            "rating_pcts": {
                k: round(v / len(loans) * 100, 1)
                for k, v in rating_counts.items()
            },
        }

    # ------------------------------------------------------------------
    # Static mapping helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pd_to_likelihood(pd: float) -> LikelihoodLevel:
        """Map P(default) to a LikelihoodLevel.

        Args:
            pd: Probability of default in [0, 1].

        Returns:
            Corresponding LikelihoodLevel.
        """
        if pd < 0.05:
            return LikelihoodLevel.RARE
        elif pd < 0.15:
            return LikelihoodLevel.UNLIKELY
        elif pd < 0.35:
            return LikelihoodLevel.POSSIBLE
        elif pd < 0.65:
            return LikelihoodLevel.LIKELY
        else:
            return LikelihoodLevel.ALMOST_CERTAIN

    @staticmethod
    def _exposure_to_impact(amount: float) -> ImpactLevel:
        """Map loan amount (exposure) to an ImpactLevel.

        Args:
            amount: Loan exposure in currency units.

        Returns:
            Corresponding ImpactLevel.
        """
        if amount < 10_000:
            return ImpactLevel.NEGLIGIBLE
        elif amount < 50_000:
            return ImpactLevel.MINOR
        elif amount < 200_000:
            return ImpactLevel.MODERATE
        elif amount < 1_000_000:
            return ImpactLevel.MAJOR
        else:
            return ImpactLevel.CATASTROPHIC

    def _build_matrix(self) -> Dict[int, Dict[int, RiskCell]]:
        """Pre-build the 5×5 matrix of RiskCell objects.

        Returns:
            Nested dict: cells[likelihood_val][impact_val] = RiskCell.
        """
        cells: Dict[int, Dict[int, RiskCell]] = {}
        for lv in range(1, 6):
            cells[lv] = {}
            for iv in range(1, 6):
                cells[lv][iv] = RiskCell(
                    likelihood=LikelihoodLevel(lv),
                    impact=ImpactLevel(iv),
                )
        return cells
