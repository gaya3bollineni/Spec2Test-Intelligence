import pytest

from app.ui.helpers import generate_spec2test_results


def test_manual_pipeline_generates_test_cases() -> None:
    (
        test_cases,
        parsed_items,
        requirement_analysis,
        completeness_analysis,
        traceability_rows,
    ) = generate_spec2test_results(
        acceptance_criteria=(
            "User can log in with valid credentials."
        )
    )

    assert len(parsed_items) == 1
    assert parsed_items[0].id == "AC-001"
    assert parsed_items[0].priority == "Medium"

    assert len(test_cases) == 3

    assert all(
        test_case.requirement_id == "AC-001"
        for test_case in test_cases
    )

    assert len(traceability_rows) == 1

    assert (
        traceability_rows[0].requirement_id
        == "AC-001"
    )

    assert requirement_analysis is not None
    assert completeness_analysis is not None


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

    (
        test_cases,
        parsed_items,
        _requirement_analysis,
        _completeness_analysis,
        traceability_rows,
    ) = generate_spec2test_results(
        requirement_records=requirement_records
    )

    assert len(parsed_items) == 1

    assert parsed_items[0].id == "REQ-101"
    assert parsed_items[0].priority == "Critical"

    assert len(test_cases) == 3

    assert all(
        test_case.requirement_id == "REQ-101"
        for test_case in test_cases
    )

    assert all(
        test_case.priority == "Critical"
        for test_case in test_cases
    )

    assert len(traceability_rows) == 1

    assert (
        traceability_rows[0].requirement_id
        == "REQ-101"
    )


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

    (
        test_cases,
        parsed_items,
        _requirement_analysis,
        _completeness_analysis,
        traceability_rows,
    ) = generate_spec2test_results(
        requirement_records=requirement_records
    )

    assert len(parsed_items) == 2
    assert len(test_cases) == 6
    assert len(traceability_rows) == 2

    requirement_ids = {
        test_case.requirement_id
        for test_case in test_cases
    }

    assert requirement_ids == {
        "REQ-201",
        "REQ-202",
    }


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