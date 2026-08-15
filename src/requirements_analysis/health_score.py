from dataclasses import dataclass
from typing import Any, List

from src.models.schemas import ParsedCriterion


@dataclass
class RequirementHealth:
    requirement_id: str
    requirement_text: str

    completeness_score: int
    clarity_score: int
    uniqueness_score: int
    consistency_score: int
    dependency_score: int

    overall_score: int
    rating: str

    deductions: List[str]


class RequirementHealthScorer:
    """
    Produces deterministic, explainable health scores.
    """

    def calculate(
        self,
        parsed_items: List[ParsedCriterion],
        requirement_analysis: Any,
        completeness_analysis: Any,
        duplicate_requirements: list[Any],
        conflicting_requirements: list[Any],
        dependencies: list[Any],
    ) -> List[RequirementHealth]:

        results: List[RequirementHealth] = []

        for item in parsed_items:
            deductions: List[str] = []

            completeness_score = (
                self._get_completeness_score(
                    item.id,
                    completeness_analysis,
                )
            )

            clarity_score = self._calculate_clarity(
                item.id,
                requirement_analysis,
            )

            uniqueness_score = self._calculate_uniqueness(
                item.id,
                duplicate_requirements,
            )

            consistency_score = self._calculate_consistency(
                item.id,
                conflicting_requirements,
            )

            dependency_score = self._calculate_dependency_score(
                item.id,
                dependencies,
            )

            if clarity_score < 100:
                deductions.append(
                    "Ambiguous wording was detected."
                )

            if uniqueness_score < 100:
                deductions.append(
                    "Requirement duplicates another requirement."
                )

            if consistency_score < 100:
                deductions.append(
                    "Requirement conflicts with another requirement."
                )

            if dependency_score < 100:
                deductions.append(
                    "Requirement has one or more detected dependencies."
                )

            if completeness_score < 100:
                deductions.append(
                    "Requirement is missing one or more completeness elements."
                )

            overall_score = round(
                completeness_score * 0.40
                + clarity_score * 0.25
                + uniqueness_score * 0.15
                + consistency_score * 0.15
                + dependency_score * 0.05
            )

            results.append(
                RequirementHealth(
                    requirement_id=item.id,
                    requirement_text=item.raw_text,
                    completeness_score=completeness_score,
                    clarity_score=clarity_score,
                    uniqueness_score=uniqueness_score,
                    consistency_score=consistency_score,
                    dependency_score=dependency_score,
                    overall_score=overall_score,
                    rating=self._get_rating(
                        overall_score
                    ),
                    deductions=deductions,
                )
            )

        return results

    @staticmethod
    def _get_completeness_score(
        requirement_id: str,
        completeness_analysis: Any,
    ) -> int:
        for result in completeness_analysis.criterion_results:
            if result.criterion_id == requirement_id:
                return result.completeness_score

        return 0

    @staticmethod
    def _calculate_clarity(
        requirement_id: str,
        requirement_analysis: Any,
    ) -> int:
        warning_count = sum(
            warning.criterion_id == requirement_id
            for warning in requirement_analysis.warnings
        )

        return max(
            0,
            100 - warning_count * 20,
        )

    @staticmethod
    def _calculate_uniqueness(
        requirement_id: str,
        duplicates: list[Any],
    ) -> int:
        found = any(
            duplicate.requirement_id == requirement_id
            for duplicate in duplicates
        )

        return 40 if found else 100

    @staticmethod
    def _calculate_consistency(
        requirement_id: str,
        conflicts: list[Any],
    ) -> int:
        found = any(
            conflict.requirement_id == requirement_id
            or conflict.conflicts_with == requirement_id
            for conflict in conflicts
        )

        return 30 if found else 100

    @staticmethod
    def _calculate_dependency_score(
        requirement_id: str,
        dependencies: list[Any],
    ) -> int:
        count = sum(
            dependency.requirement_id == requirement_id
            for dependency in dependencies
        )

        return max(
            70,
            100 - count * 10,
        )

    @staticmethod
    def _get_rating(
        score: int,
    ) -> str:
        if score >= 90:
            return "Excellent"

        if score >= 75:
            return "Good"

        if score >= 60:
            return "Needs Review"

        return "Poor"