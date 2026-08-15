from types import SimpleNamespace

from src.models.schemas import ParsedCriterion
from src.requirements_analysis.health_score import (
    RequirementHealthScorer,
)


def build_requirement() -> ParsedCriterion:
    return ParsedCriterion(
        id="REQ-001",
        raw_text=(
            "User should log in with valid credentials."
        ),
        actor="user",
        action="log in",
        condition="with valid credentials",
        expected_outcome=(
            "User should log in successfully."
        ),
        rule_type="functional",
        priority="High",
    )


def test_healthy_requirement_receives_high_score() -> None:
    scorer = RequirementHealthScorer()

    requirement = build_requirement()

    requirement_analysis = SimpleNamespace(
        warnings=[]
    )

    completeness_analysis = SimpleNamespace(
        criterion_results=[
            SimpleNamespace(
                criterion_id="REQ-001",
                completeness_score=100,
            )
        ]
    )

    results = scorer.calculate(
        parsed_items=[requirement],
        requirement_analysis=requirement_analysis,
        completeness_analysis=completeness_analysis,
        duplicate_requirements=[],
        conflicting_requirements=[],
        dependencies=[],
    )

    assert len(results) == 1

    health = results[0]

    assert health.overall_score == 100
    assert health.rating == "Excellent"


def test_duplicate_reduces_health_score() -> None:
    scorer = RequirementHealthScorer()

    requirement = build_requirement()

    requirement_analysis = SimpleNamespace(
        warnings=[]
    )

    completeness_analysis = SimpleNamespace(
        criterion_results=[
            SimpleNamespace(
                criterion_id="REQ-001",
                completeness_score=100,
            )
        ]
    )

    duplicate = SimpleNamespace(
        requirement_id="REQ-001"
    )

    results = scorer.calculate(
        parsed_items=[requirement],
        requirement_analysis=requirement_analysis,
        completeness_analysis=completeness_analysis,
        duplicate_requirements=[duplicate],
        conflicting_requirements=[],
        dependencies=[],
    )

    health = results[0]

    assert health.uniqueness_score == 40
    assert health.overall_score < 100


def test_conflict_reduces_consistency_score() -> None:
    scorer = RequirementHealthScorer()

    requirement = build_requirement()

    requirement_analysis = SimpleNamespace(
        warnings=[]
    )

    completeness_analysis = SimpleNamespace(
        criterion_results=[
            SimpleNamespace(
                criterion_id="REQ-001",
                completeness_score=100,
            )
        ]
    )

    conflict = SimpleNamespace(
        requirement_id="REQ-001",
        conflicts_with="REQ-002",
    )

    results = scorer.calculate(
        parsed_items=[requirement],
        requirement_analysis=requirement_analysis,
        completeness_analysis=completeness_analysis,
        duplicate_requirements=[],
        conflicting_requirements=[conflict],
        dependencies=[],
    )

    health = results[0]

    assert health.consistency_score == 30
    assert health.overall_score < 100