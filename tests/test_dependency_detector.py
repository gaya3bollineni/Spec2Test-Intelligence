from src.models.schemas import ParsedCriterion
from src.requirements_analysis.dependency_detector import (
    RequirementDependencyDetector,
)


def build_requirement(
    requirement_id: str,
    text: str,
) -> ParsedCriterion:
    return ParsedCriterion(
        id=requirement_id,
        raw_text=text,
        actor="user",
        action=None,
        condition=None,
        expected_outcome=text,
        rule_type="functional",
        priority="Medium",
    )


def test_dashboard_depends_on_login() -> None:
    detector = RequirementDependencyDetector()

    requirements = [
        build_requirement(
            "REQ-001",
            "User should log in with valid credentials.",
        ),
        build_requirement(
            "REQ-002",
            "User should view the dashboard.",
        ),
    ]

    dependencies = detector.detect(requirements)

    assert len(dependencies) == 1

    dependency = dependencies[0]

    assert dependency.requirement_id == "REQ-002"
    assert dependency.depends_on == "REQ-001"


def test_no_dependency_for_unrelated_requirements() -> None:
    detector = RequirementDependencyDetector()

    requirements = [
        build_requirement(
            "REQ-001",
            "User should upload a document.",
        ),
        build_requirement(
            "REQ-002",
            "System should display an error message.",
        ),
    ]

    dependencies = detector.detect(requirements)

    assert dependencies == []