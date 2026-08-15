from src.models.schemas import ParsedCriterion
from src.requirements_analysis.conflict_detector import (
    ConflictRequirementDetector,
)


def build_requirement(
    requirement_id: str,
    text: str,
) -> ParsedCriterion:
    return ParsedCriterion(
        id=requirement_id,
        raw_text=text,
        actor="system",
        action="allow guest checkout",
        condition=None,
        expected_outcome=text,
        rule_type="functional",
        priority="Medium",
    )


def test_detects_direct_conflict() -> None:
    detector = ConflictRequirementDetector()

    requirements = [
        build_requirement(
            "AC-001",
            "System should allow guest checkout.",
        ),
        build_requirement(
            "AC-002",
            "System should not allow guest checkout.",
        ),
    ]

    conflicts = detector.detect(
        requirements
    )

    assert len(conflicts) == 1

    assert (
        conflicts[0].requirement_id
        == "AC-002"
    )

    assert (
        conflicts[0].conflicts_with
        == "AC-001"
    )


def test_non_conflicting_requirements() -> None:
    detector = ConflictRequirementDetector()

    requirements = [
        build_requirement(
            "AC-001",
            "System should allow guest checkout.",
        ),
        build_requirement(
            "AC-002",
            "System should allow registered checkout.",
        ),
    ]

    conflicts = detector.detect(
        requirements
    )

    assert conflicts == []