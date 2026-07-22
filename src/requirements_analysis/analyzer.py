from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.models.schemas import ParsedCriterion


@dataclass
class RequirementIssue:
    criterion_id: str
    issue_type: str
    message: str
    recommendation: str


@dataclass
class RequirementAnalysisResult:
    total_criteria: int
    quality_score: int
    ambiguous_criteria_count: int
    warnings: List[RequirementIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class RequirementAnalyzer:
    """
    Performs deterministic requirement quality analysis.

    This module does not use an LLM or external AI API.
    It applies explainable rules to identify ambiguous wording
    and calculate a requirement quality score.
    """

    AMBIGUOUS_WORDS = {
        "quickly": "Replace 'quickly' with a measurable response time.",
        "properly": "Describe the exact expected system behavior.",
        "appropriately": "Define the expected response or validation clearly.",
        "efficiently": "Add a measurable performance or processing target.",
        "normally": "Describe the specific normal condition or workflow.",
        "correctly": "State the exact expected result.",
        "user-friendly": "Define measurable usability expectations.",
        "fast": "Specify the required response time.",
        "secure": "Specify the required security controls.",
        "seamlessly": "Describe the expected integration behavior.",
    }

    def analyze(
        self,
        parsed_criteria: List[ParsedCriterion],
    ) -> RequirementAnalysisResult:
        warnings: List[RequirementIssue] = []
        recommendations: List[str] = []
        ambiguous_criterion_ids = set()

        for criterion in parsed_criteria:
            criterion_text = criterion.raw_text.lower()

            for ambiguous_word, recommendation in self.AMBIGUOUS_WORDS.items():
                if ambiguous_word in criterion_text:
                    warnings.append(
                        RequirementIssue(
                            criterion_id=criterion.id,
                            issue_type="Ambiguous wording",
                            message=(
                                f"Acceptance criterion contains the ambiguous "
                                f"term '{ambiguous_word}'."
                            ),
                            recommendation=recommendation,
                        )
                    )

                    ambiguous_criterion_ids.add(criterion.id)

                    if recommendation not in recommendations:
                        recommendations.append(recommendation)

        total_criteria = len(parsed_criteria)

        quality_score = self.calculate_quality_score(
            total_criteria=total_criteria,
            warning_count=len(warnings),
        )

        return RequirementAnalysisResult(
            total_criteria=total_criteria,
            quality_score=quality_score,
            ambiguous_criteria_count=len(ambiguous_criterion_ids),
            warnings=warnings,
            recommendations=recommendations,
        )

    @staticmethod
    def calculate_quality_score(
        total_criteria: int,
        warning_count: int,
    ) -> int:
        if total_criteria == 0:
            return 0

        maximum_score = 100

        penalty_per_warning = max(
            5,
            round(30 / total_criteria),
        )

        total_penalty = warning_count * penalty_per_warning

        return max(
            0,
            maximum_score - total_penalty,
        )