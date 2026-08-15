import pytest

from app.ui.helpers import generate_spec2test_results


def test_manual_pipeline_generates_test_cases() -> None:
    result = generate_spec2test_results(
        acceptance_criteria=(
            "User can log in with valid credentials."
        )
    )

    assert len(result.parsed_items) == 1

    assert result.parsed_items[0].id == "AC-001"
    assert result.parsed_items[0].priority == "Medium"

    # Manual requirements default to Medium:
    # Positive + Negative + Edge
    assert len(result.test_cases) == 3

    assert all(
        test_case.requirement_id == "AC-001"
        for test_case in result.test_cases
    )

    assert len(result.traceability_rows) == 1

    traceability = result.traceability_rows[0]

    assert traceability.requirement_id == "AC-001"
    assert traceability.total_test_cases == 3
    assert traceability.expected_test_cases == 3
    assert traceability.coverage_percentage == 100

    assert result.requirement_analysis is not None
    assert result.completeness_analysis is not None

    assert result.duplicate_requirements == []
    assert result.conflicting_requirements == []


def test_excel_pipeline_preserves_metadata() -> None:
    requirement_records = [
        {
            "requirement_id": "REQ-101",
            "acceptance_criteria": (
                "User can submit a valid application."
            ),
            "priority": "Critical",
        }
    ]

    result = generate_spec2test_results(
        requirement_records=requirement_records
    )

    assert len(result.parsed_items) == 1

    assert result.parsed_items[0].id == "REQ-101"
    assert (
        result.parsed_items[0].priority
        == "Critical"
    )

    # Critical:
    # Positive + Negative + Edge + Boundary + Security
    assert len(result.test_cases) == 5

    assert all(
        test_case.requirement_id == "REQ-101"
        for test_case in result.test_cases
    )

    assert all(
        test_case.priority == "Critical"
        for test_case in result.test_cases
    )

    assert {
        test_case.scenario_type
        for test_case in result.test_cases
    } == {
        "Positive",
        "Negative",
        "Edge",
        "Boundary",
        "Security",
    }

    assert len(result.traceability_rows) == 1

    traceability = result.traceability_rows[0]

    assert traceability.requirement_id == "REQ-101"
    assert traceability.total_test_cases == 5
    assert traceability.expected_test_cases == 5
    assert traceability.coverage_percentage == 100

    assert result.duplicate_requirements == []
    assert result.conflicting_requirements == []


def test_pipeline_handles_multiple_excel_requirements() -> None:
    requirement_records = [
        {
            "requirement_id": "REQ-201",
            "acceptance_criteria": (
                "Customer can upload a document."
            ),
            "priority": "High",
        },
        {
            "requirement_id": "REQ-202",
            "acceptance_criteria": (
                "Customer can download a document."
            ),
            "priority": "Low",
        },
    ]

    result = generate_spec2test_results(
        requirement_records=requirement_records
    )

    assert len(result.parsed_items) == 2

    # High = 4
    # Low = 2
    assert len(result.test_cases) == 6

    assert len(result.traceability_rows) == 2

    requirement_ids = {
        test_case.requirement_id
        for test_case in result.test_cases
    }

    assert requirement_ids == {
        "REQ-201",
        "REQ-202",
    }

    high_cases = [
        test_case
        for test_case in result.test_cases
        if test_case.requirement_id == "REQ-201"
    ]

    low_cases = [
        test_case
        for test_case in result.test_cases
        if test_case.requirement_id == "REQ-202"
    ]

    assert len(high_cases) == 4
    assert len(low_cases) == 2

    assert all(
        test_case.priority == "High"
        for test_case in high_cases
    )

    assert all(
        test_case.priority == "Low"
        for test_case in low_cases
    )

    assert result.duplicate_requirements == []
    assert result.conflicting_requirements == []


def test_pipeline_rejects_empty_input() -> None:
    with pytest.raises(
        ValueError,
        match="No valid requirements",
    ):
        generate_spec2test_results()


def test_pipeline_rejects_blank_manual_input() -> None:
    with pytest.raises(
        ValueError,
        match="No valid requirements",
    ):
        generate_spec2test_results(
            acceptance_criteria="   "
        )


def test_pipeline_detects_duplicate_requirements() -> None:
    acceptance_criteria = """
    1. User should be able to log in with valid credentials.
    2. System should display an error for invalid credentials.
    3. User should be able to log in with valid credentials.
    """

    result = generate_spec2test_results(
        acceptance_criteria=acceptance_criteria
    )

    assert len(
        result.duplicate_requirements
    ) == 1

    duplicate = (
        result.duplicate_requirements[0]
    )

    assert duplicate.requirement_id == "AC-003"
    assert duplicate.duplicate_of == "AC-001"

    assert result.conflicting_requirements == []


def test_pipeline_detects_conflicting_requirements() -> None:
    acceptance_criteria = """
    1. System should allow guest checkout.
    2. System should not allow guest checkout.
    """

    result = generate_spec2test_results(
        acceptance_criteria=acceptance_criteria
    )

    assert len(
        result.conflicting_requirements
    ) == 1

    conflict = (
        result.conflicting_requirements[0]
    )

    assert conflict.requirement_id == "AC-002"
    assert conflict.conflicts_with == "AC-001"


def test_pipeline_handles_duplicate_and_conflict_together() -> None:
    acceptance_criteria = """
    1. User should be able to log in with valid credentials.
    2. User should be able to log in with valid credentials.
    3. System should allow guest checkout.
    4. System should not allow guest checkout.
    """

    result = generate_spec2test_results(
        acceptance_criteria=acceptance_criteria
    )

    assert len(
        result.duplicate_requirements
    ) == 1

    assert len(
        result.conflicting_requirements
    ) == 1

    duplicate = (
        result.duplicate_requirements[0]
    )

    conflict = (
        result.conflicting_requirements[0]
    )

    assert duplicate.requirement_id == "AC-002"
    assert duplicate.duplicate_of == "AC-001"

    assert conflict.requirement_id == "AC-004"
    assert conflict.conflicts_with == "AC-003"


def test_pipeline_generates_traceability_for_each_requirement() -> None:
    acceptance_criteria = """
    1. User should be able to log in with valid credentials.
    2. User should be able to reset password.
    """

    result = generate_spec2test_results(
        acceptance_criteria=acceptance_criteria
    )

    assert len(
        result.traceability_rows
    ) == 2

    first_row = (
        result.traceability_rows[0]
    )

    second_row = (
        result.traceability_rows[1]
    )

    assert first_row.requirement_id == "AC-001"
    assert second_row.requirement_id == "AC-002"

    assert first_row.total_test_cases == 3
    assert second_row.total_test_cases == 3

    assert first_row.expected_test_cases == 3
    assert second_row.expected_test_cases == 3

    assert first_row.coverage_percentage == 100
    assert second_row.coverage_percentage == 100


def test_pipeline_preserves_excel_requirement_ids_in_traceability() -> None:
    requirement_records = [
        {
            "requirement_id": "BANK-001",
            "acceptance_criteria": (
                "Customer can submit a loan application."
            ),
            "priority": "High",
        },
        {
            "requirement_id": "BANK-002",
            "acceptance_criteria": (
                "System can generate a loan decision."
            ),
            "priority": "Critical",
        },
    ]

    result = generate_spec2test_results(
        requirement_records=requirement_records
    )

    traceability_ids = {
        row.requirement_id
        for row in result.traceability_rows
    }

    assert traceability_ids == {
        "BANK-001",
        "BANK-002",
    }

    first = next(
        row
        for row in result.traceability_rows
        if row.requirement_id == "BANK-001"
    )

    second = next(
        row
        for row in result.traceability_rows
        if row.requirement_id == "BANK-002"
    )

    assert first.total_test_cases == 4
    assert first.expected_test_cases == 4

    assert second.total_test_cases == 5
    assert second.expected_test_cases == 5


def test_pipeline_detects_requirement_dependencies() -> None:
    acceptance_criteria = """
    1. User should log in with valid credentials.
    2. User should view the dashboard.
    """

    result = generate_spec2test_results(
        acceptance_criteria=acceptance_criteria
    )

    assert len(
        result.dependencies
    ) == 1

    dependency = result.dependencies[0]

    assert (
        dependency.requirement_id
        == "AC-002"
    )

    assert (
        dependency.depends_on
        == "AC-001"
    )


def test_pipeline_generates_health_scores() -> None:
    result = generate_spec2test_results(
        acceptance_criteria=(
            "User should be able to log in "
            "with valid credentials."
        )
    )

    assert len(
        result.health_scores
    ) == 1

    health = result.health_scores[0]

    assert (
        health.requirement_id
        == "AC-001"
    )

    assert (
        0
        <= health.overall_score
        <= 100
    )

    assert health.rating in {
        "Excellent",
        "Good",
        "Needs Review",
        "Poor",
    }


def test_risk_based_generation_by_priority() -> None:
    requirement_records = [
        {
            "requirement_id": "LOW-001",
            "acceptance_criteria": (
                "User can view help content."
            ),
            "priority": "Low",
        },
        {
            "requirement_id": "MED-001",
            "acceptance_criteria": (
                "User can update profile."
            ),
            "priority": "Medium",
        },
        {
            "requirement_id": "HIGH-001",
            "acceptance_criteria": (
                "Customer can submit an application."
            ),
            "priority": "High",
        },
        {
            "requirement_id": "CRIT-001",
            "acceptance_criteria": (
                "System can approve a transaction."
            ),
            "priority": "Critical",
        },
    ]

    result = generate_spec2test_results(
        requirement_records=requirement_records
    )

    counts = {}

    for test_case in result.test_cases:
        counts[
            test_case.requirement_id
        ] = (
            counts.get(
                test_case.requirement_id,
                0,
            )
            + 1
        )

    assert counts["LOW-001"] == 2
    assert counts["MED-001"] == 3
    assert counts["HIGH-001"] == 4
    assert counts["CRIT-001"] == 5