from typing import Any

from src.ingestion.normalizer import InputNormalizer
from src.parsing.criteria_parser import CriteriaParser
from src.requirements_analysis.analyzer import RequirementAnalyzer
from src.requirements_analysis.completeness_analyzer import (
    CompletenessAnalyzer,
)
from src.traceability.matrix_builder import (
    TraceabilityMatrixBuilder,
)
from src.scenario_expander.expander import ScenarioExpander


def generate_spec2test_results(
    acceptance_criteria: str,
) -> tuple[
    list[Any],
    list[Any],
    Any,
    Any,
]:
    normalizer = InputNormalizer()
    parser = CriteriaParser()
    requirement_analyzer = RequirementAnalyzer()
    completeness_analyzer = CompletenessAnalyzer()
    scenario_expander = ScenarioExpander()
    traceability_builder = TraceabilityMatrixBuilder()

    normalized_items = normalizer.normalize(
        acceptance_criteria
    )

    parsed_items = parser.parse(
        normalized_items
    )

    requirement_analysis = requirement_analyzer.analyze(
        parsed_items
    )

    completeness_analysis = completeness_analyzer.analyze(
        parsed_items
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