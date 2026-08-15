from typing import Any

from src.ingestion.normalizer import InputNormalizer
from src.models.pipeline_result import PipelineResult
from src.parsing.criteria_parser import CriteriaParser
from src.requirements_analysis.analyzer import RequirementAnalyzer
from src.requirements_analysis.completeness_analyzer import (
    CompletenessAnalyzer,
)
from src.requirements_analysis.conflict_detector import (
    ConflictRequirementDetector,
)
from src.requirements_analysis.dependency_detector import (
    RequirementDependencyDetector,
)
from src.requirements_analysis.duplicate_detector import (
    DuplicateRequirementDetector,
)
from src.requirements_analysis.health_score import (
    RequirementHealthScorer,
)
from src.scenario_expander.expander import ScenarioExpander
from src.traceability.matrix_builder import (
    TraceabilityMatrixBuilder,
)


def generate_spec2test_results(
    acceptance_criteria: str | None = None,
    requirement_records: list[dict[str, Any]] | None = None,
) -> PipelineResult:

    normalizer = InputNormalizer()
    parser = CriteriaParser()

    requirement_analyzer = RequirementAnalyzer()
    completeness_analyzer = CompletenessAnalyzer()
    duplicate_detector = DuplicateRequirementDetector()
    conflict_detector = ConflictRequirementDetector()
    dependency_detector = RequirementDependencyDetector()
    health_scorer = RequirementHealthScorer()

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

    duplicate_requirements = (
        duplicate_detector.detect(
            parsed_items
        )
    )

    conflicting_requirements = (
        conflict_detector.detect(
            parsed_items
        )
    )

    dependencies = (
        dependency_detector.detect(
            parsed_items
        )
    )

    health_scores = (
        health_scorer.calculate(
            parsed_items=parsed_items,
            requirement_analysis=requirement_analysis,
            completeness_analysis=completeness_analysis,
            duplicate_requirements=duplicate_requirements,
            conflicting_requirements=conflicting_requirements,
            dependencies=dependencies,
        )
    )

    test_cases = scenario_expander.generate(
        parsed_items
    )

    traceability_rows = (
        traceability_builder.build(
            parsed_items=parsed_items,
            test_cases=test_cases,
        )
    )

    return PipelineResult(
        test_cases=test_cases,
        parsed_items=parsed_items,
        requirement_analysis=requirement_analysis,
        completeness_analysis=completeness_analysis,
        traceability_rows=traceability_rows,
        duplicate_requirements=duplicate_requirements,
        conflicting_requirements=conflicting_requirements,
        dependencies=dependencies,
        health_scores=health_scores,
    )