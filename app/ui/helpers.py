from typing import Any

from src.ingestion.normalizer import InputNormalizer
from src.parsing.criteria_parser import CriteriaParser
from src.requirements_analysis.analyzer import (
    RequirementAnalyzer,
)
from src.requirements_analysis.completeness_analyzer import (
    CompletenessAnalyzer,
)
from src.scenario_expander.expander import (
    ScenarioExpander,
)
from src.traceability.matrix_builder import (
    TraceabilityMatrixBuilder,
)


def generate_spec2test_results(
    acceptance_criteria: str | None = None,
    requirement_records: list[dict[str, Any]] | None = None,
) -> tuple[
    list[Any],
    list[Any],
    Any,
    Any,
    list[Any],
]:
    """
    Runs the Spec2Test processing pipeline.

    Supports either:
    - manually entered acceptance-criteria text
    - structured requirement records imported from Excel
    """

    normalizer = InputNormalizer()
    parser = CriteriaParser()
    requirement_analyzer = RequirementAnalyzer()
    completeness_analyzer = CompletenessAnalyzer()
    scenario_expander = ScenarioExpander()
    traceability_builder = TraceabilityMatrixBuilder()

    if requirement_records:
        normalized_items = normalizer.normalize_records(
            requirement_records
        )
    elif acceptance_criteria and acceptance_criteria.strip():
        normalized_items = normalizer.normalize(
            acceptance_criteria
        )
    else:
        raise ValueError(
            "No valid requirements were provided."
        )

    if not normalized_items:
        raise ValueError(
            "No valid requirements were found after normalization."
        )

    parsed_items = parser.parse(
        normalized_items
    )

    requirement_analysis = (
        requirement_analyzer.analyze(
            parsed_items
        )
    )

    completeness_analysis = (
        completeness_analyzer.analyze(
            parsed_items
        )
    )

    test_cases = scenario_expander.generate(
        parsed_items
    )

    traceability_rows = traceability_builder.build(
        parsed_items=parsed_items,
        test_cases=test_cases,
    )

    return (
        test_cases,
        parsed_items,
        requirement_analysis,
        completeness_analysis,
        traceability_rows,
    )