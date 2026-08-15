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
    boundary_count: int
    security_count: int

    total_test_cases: int
    expected_test_cases: int

    coverage_percentage: int
    coverage_status: str


class TraceabilityMatrixBuilder:

    EXPECTED_BY_PRIORITY = {
        "Low": 2,
        "Medium": 3,
        "High": 4,
        "Critical": 5,
    }

    def build(
        self,
        parsed_items: List[ParsedCriterion],
        test_cases: List[TestCase],
    ) -> List[TraceabilityRow]:

        rows: List[TraceabilityRow] = []

        for criterion in parsed_items:

            related = [
                test_case
                for test_case in test_cases
                if test_case.requirement_id
                == criterion.id
            ]

            def count_type(
                scenario_type: str,
            ) -> int:
                return sum(
                    test_case.scenario_type
                    == scenario_type
                    for test_case in related
                )

            expected = (
                self.EXPECTED_BY_PRIORITY.get(
                    criterion.priority,
                    3,
                )
            )

            total = len(related)

            coverage = round(
                total / expected * 100
            ) if expected else 0

            coverage = min(
                coverage,
                100,
            )

            rows.append(
                TraceabilityRow(
                    requirement_id=criterion.id,
                    acceptance_criteria=(
                        criterion.raw_text
                    ),
                    positive_count=count_type(
                        "Positive"
                    ),
                    negative_count=count_type(
                        "Negative"
                    ),
                    edge_count=count_type(
                        "Edge"
                    ),
                    boundary_count=count_type(
                        "Boundary"
                    ),
                    security_count=count_type(
                        "Security"
                    ),
                    total_test_cases=total,
                    expected_test_cases=expected,
                    coverage_percentage=coverage,
                    coverage_status=(
                        self._status(
                            coverage
                        )
                    ),
                )
            )

        return rows

    @staticmethod
    def _status(
        coverage: int,
    ) -> str:

        if coverage == 100:
            return "Fully Covered"

        if coverage >= 67:
            return "Partially Covered"

        if coverage > 0:
            return "Low Coverage"

        return "Not Covered"