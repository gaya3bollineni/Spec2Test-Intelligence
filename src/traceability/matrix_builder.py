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


class TraceabilityMatrixBuilder:
    """
    Builds a Requirement Traceability Matrix (RTM)
    from parsed acceptance criteria and generated test cases.
    """

    EXPECTED_TEST_CASES_PER_REQUIREMENT = 3

    def build(
        self,
        parsed_items: List[ParsedCriterion],
        test_cases: List[TestCase],
    ) -> List[TraceabilityRow]:

        rows: List[TraceabilityRow] = []

        for criterion in parsed_items:

            related = [
                tc
                for tc in test_cases
                if tc.requirement_id == criterion.id
            ]

            positive = sum(
                tc.scenario_type == "Positive"
                for tc in related
            )

            negative = sum(
                tc.scenario_type == "Negative"
                for tc in related
            )

            edge = sum(
                tc.scenario_type == "Edge"
                for tc in related
            )

            total = len(related)

            coverage = round(
                (
                    total
                    / self.EXPECTED_TEST_CASES_PER_REQUIREMENT
                )
                * 100
            )

            coverage = min(coverage, 100)

            rows.append(
                TraceabilityRow(
                    requirement_id=criterion.id,
                    acceptance_criteria=criterion.raw_text,
                    positive_count=positive,
                    negative_count=negative,
                    edge_count=edge,
                    total_test_cases=total,
                    coverage_percentage=coverage,
                )
            )

        return rows