import io
import json
from typing import Any

import pandas as pd
import streamlit as st

from app.config import (
    EXCEL_FILE_NAME,
    EXCEL_SHEET_NAME,
    JSON_FILE_NAME,
)


def build_export_dataframe(
    test_cases: list[Any],
    include_preconditions: bool,
) -> pd.DataFrame:
    rows = []

    for test_case in test_cases:
        row = {
            "Test Case ID": test_case.test_case_id,
            "Requirement ID": test_case.requirement_id,
            "Scenario Type": test_case.scenario_type,
            "Test Scenario": test_case.test_scenario,
            "Description": test_case.test_case_description,
            "Test Steps": "\n".join(
                f"{index}. {step}"
                for index, step in enumerate(
                    test_case.test_steps,
                    start=1,
                )
            ),
            "Test Data": test_case.test_data,
            "Expected Result": test_case.expected_result,
            "Priority": test_case.priority,
        }

        if include_preconditions:
            row["Preconditions"] = "\n".join(
                f"{index}. {precondition}"
                for index, precondition in enumerate(
                    test_case.preconditions,
                    start=1,
                )
            )

        rows.append(row)

    return pd.DataFrame(rows)


def create_excel_file(
    dataframe: pd.DataFrame,
) -> io.BytesIO:
    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl",
    ) as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name=EXCEL_SHEET_NAME,
        )

        worksheet = writer.sheets[EXCEL_SHEET_NAME]

        for column_cells in worksheet.columns:
            column_letter = column_cells[0].column_letter

            maximum_length = max(
                (
                    len(str(cell.value))
                    for cell in column_cells
                    if cell.value is not None
                ),
                default=0,
            )

            worksheet.column_dimensions[column_letter].width = min(
                maximum_length + 2,
                50,
            )

        for row_cells in worksheet.iter_rows():
            for cell in row_cells:
                cell.alignment = cell.alignment.copy(
                    wrap_text=True,
                    vertical="top",
                )

    excel_buffer.seek(0)

    return excel_buffer


def create_json_output(
    test_cases: list[Any],
) -> str:
    return json.dumps(
        [
            test_case.model_dump()
            for test_case in test_cases
        ],
        indent=2,
    )


def show_export_buttons(
    test_cases: list[Any],
    include_preconditions: bool,
) -> None:
    dataframe = build_export_dataframe(
        test_cases=test_cases,
        include_preconditions=include_preconditions,
    )

    json_output = create_json_output(test_cases)
    excel_output = create_excel_file(dataframe)

    json_column, excel_column = st.columns(2)

    with json_column:
        st.download_button(
            label="Download JSON",
            data=json_output,
            file_name=JSON_FILE_NAME,
            mime="application/json",
            use_container_width=True,
        )

    with excel_column:
        st.download_button(
            label="Download Excel",
            data=excel_output,
            file_name=EXCEL_FILE_NAME,
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
        )