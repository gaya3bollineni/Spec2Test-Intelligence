from dataclasses import dataclass
from typing import List

from src.models.schemas import ParsedCriterion, TestCase


@dataclass
class TraceabilityRow:
    requirement_id: str
    acceptance_criteria: str
    positive_count: int
    negative_count: int
    edge_count: int
    total_test_cases: int
    coverage_percentage: int
    coverage_status: str


class TraceabilityMatrixBuilder:
    """
    Builds a Requirement Traceability Matrix from parsed
    acceptance criteria and generated test cases.
    """

    EXPECTED_TEST_CASES_PER_REQUIREMENT = 3

    def build(
        self,
        parsed_items: List[ParsedCriterion],
        test_cases: List[TestCase],
    ) -> List[TraceabilityRow]:
        rows: List[TraceabilityRow] = []

        for criterion in parsed_items:
            related_test_cases = [
                test_case
                for test_case in test_cases
                if test_case.requirement_id == criterion.id
            ]

            positive_count = sum(
                test_case.scenario_type == "Positive"
                for test_case in related_test_cases
            )

            negative_count = sum(
                test_case.scenario_type == "Negative"
                for test_case in related_test_cases
            )

            edge_count = sum(
                test_case.scenario_type == "Edge"
                for test_case in related_test_cases
            )

            total_test_cases = len(
                related_test_cases
            )

            coverage_percentage = round(
                (
                    total_test_cases
                    / self.EXPECTED_TEST_CASES_PER_REQUIREMENT
                )
                * 100
            )

            coverage_percentage = min(
                coverage_percentage,
                100,
            )

            coverage_status = self._get_coverage_status(
                coverage_percentage
            )

            rows.append(
                TraceabilityRow(
                    requirement_id=criterion.id,
                    acceptance_criteria=criterion.raw_text,
                    positive_count=positive_count,
                    negative_count=negative_count,
                    edge_count=edge_count,
                    total_test_cases=total_test_cases,
                    coverage_percentage=coverage_percentage,
                    coverage_status=coverage_status,
                )
            )

        return rows

    @staticmethod
    def _get_coverage_status(
        coverage_percentage: int,
    ) -> str:
        if coverage_percentage == 100:
            return "Fully Covered"

        if coverage_percentage >= 67:
            return "Partially Covered"

        if coverage_percentage > 0:
            return "Low Coverage"

        return "Not Covered"