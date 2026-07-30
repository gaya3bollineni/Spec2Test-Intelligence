from io import BytesIO

import pandas as pd
import pytest

from src.ingestion.excel_loader import ExcelRequirementLoader


def build_excel_file(
    dataframe: pd.DataFrame,
) -> BytesIO:
    excel_file = BytesIO()

    with pd.ExcelWriter(
        excel_file,
        engine="openpyxl",
    ) as writer:
        dataframe.to_excel(
            writer,
            index=False,
        )

    excel_file.seek(0)

    return excel_file


def test_loader_reads_valid_excel_file() -> None:
    loader = ExcelRequirementLoader()

    excel_file = build_excel_file(
        pd.DataFrame(
            {
                "Requirement ID": [
                    "REQ-101",
                    "REQ-102",
                ],
                "Acceptance Criteria": [
                    "User can log in.",
                    "User can reset the password.",
                ],
                "Priority": [
                    "High",
                    "Critical",
                ],
            }
        )
    )

    dataframe = loader.load(excel_file)

    assert len(dataframe) == 2

    assert list(dataframe.columns) == [
        "requirement_id",
        "acceptance_criteria",
        "priority",
    ]

    assert dataframe.iloc[0]["requirement_id"] == (
        "REQ-101"
    )

    assert dataframe.iloc[0]["priority"] == "High"


def test_loader_generates_missing_requirement_ids() -> None:
    loader = ExcelRequirementLoader()

    excel_file = build_excel_file(
        pd.DataFrame(
            {
                "Acceptance Criteria": [
                    "User can upload a document.",
                    "User can download a document.",
                ],
                "Priority": [
                    "Medium",
                    "Low",
                ],
            }
        )
    )

    dataframe = loader.load(excel_file)

    assert dataframe.iloc[0]["requirement_id"] == (
        "REQ-001"
    )

    assert dataframe.iloc[1]["requirement_id"] == (
        "REQ-002"
    )


def test_loader_generates_id_for_blank_excel_value() -> None:
    loader = ExcelRequirementLoader()

    excel_file = build_excel_file(
        pd.DataFrame(
            {
                "Requirement ID": [
                    None,
                    "REQ-202",
                ],
                "Acceptance Criteria": [
                    "User can register.",
                    "Admin can view users.",
                ],
                "Priority": [
                    "High",
                    "Medium",
                ],
            }
        )
    )

    dataframe = loader.load(excel_file)

    assert dataframe.iloc[0]["requirement_id"] == (
        "REQ-001"
    )

    assert dataframe.iloc[1]["requirement_id"] == (
        "REQ-202"
    )


def test_loader_defaults_missing_priority_to_medium() -> None:
    loader = ExcelRequirementLoader()

    excel_file = build_excel_file(
        pd.DataFrame(
            {
                "Requirement ID": [
                    "REQ-301",
                ],
                "Acceptance Criteria": [
                    "User can search for a record.",
                ],
            }
        )
    )

    dataframe = loader.load(excel_file)

    assert dataframe.iloc[0]["priority"] == "Medium"


def test_loader_normalizes_priority_values() -> None:
    loader = ExcelRequirementLoader()

    excel_file = build_excel_file(
        pd.DataFrame(
            {
                "Requirement ID": [
                    "REQ-401",
                    "REQ-402",
                    "REQ-403",
                    "REQ-404",
                ],
                "Acceptance Criteria": [
                    "Requirement one.",
                    "Requirement two.",
                    "Requirement three.",
                    "Requirement four.",
                ],
                "Priority": [
                    "critical",
                    "HIGH",
                    " medium ",
                    "low",
                ],
            }
        )
    )

    dataframe = loader.load(excel_file)

    assert dataframe["priority"].tolist() == [
        "Critical",
        "High",
        "Medium",
        "Low",
    ]


def test_loader_defaults_invalid_priority_to_medium() -> None:
    loader = ExcelRequirementLoader()

    excel_file = build_excel_file(
        pd.DataFrame(
            {
                "Requirement ID": [
                    "REQ-501",
                ],
                "Acceptance Criteria": [
                    "User can save the form.",
                ],
                "Priority": [
                    "Urgent",
                ],
            }
        )
    )

    dataframe = loader.load(excel_file)

    assert dataframe.iloc[0]["priority"] == "Medium"


def test_loader_supports_column_aliases() -> None:
    loader = ExcelRequirementLoader()

    excel_file = build_excel_file(
        pd.DataFrame(
            {
                "ID": [
                    "REQ-601",
                ],
                "Criteria": [
                    "User can update the profile.",
                ],
                "Severity": [
                    "High",
                ],
            }
        )
    )

    dataframe = loader.load(excel_file)

    assert dataframe.iloc[0]["requirement_id"] == (
        "REQ-601"
    )

    assert dataframe.iloc[0][
        "acceptance_criteria"
    ] == "User can update the profile."

    assert dataframe.iloc[0]["priority"] == "High"


def test_loader_raises_error_when_criteria_column_missing() -> None:
    loader = ExcelRequirementLoader()

    excel_file = build_excel_file(
        pd.DataFrame(
            {
                "Requirement ID": [
                    "REQ-701",
                ],
                "Priority": [
                    "High",
                ],
            }
        )
    )

    with pytest.raises(
        ValueError,
        match="Acceptance Criteria",
    ):
        loader.load(excel_file)


def test_loader_raises_error_for_empty_workbook() -> None:
    loader = ExcelRequirementLoader()

    excel_file = build_excel_file(
        pd.DataFrame()
    )

    with pytest.raises(
        ValueError,
        match="does not contain any rows",
    ):
        loader.load(excel_file)


def test_to_records_returns_structured_requirements() -> None:
    loader = ExcelRequirementLoader()

    dataframe = pd.DataFrame(
        {
            "requirement_id": [
                "REQ-801",
            ],
            "acceptance_criteria": [
                "User can submit the form.",
            ],
            "priority": [
                "Critical",
            ],
        }
    )

    records = loader.to_records(dataframe)

    assert records == [
        {
            "requirement_id": "REQ-801",
            "acceptance_criteria": (
                "User can submit the form."
            ),
            "priority": "Critical",
        }
    ]