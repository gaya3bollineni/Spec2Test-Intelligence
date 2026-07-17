import io
import json
from typing import Any

import pandas as pd
import streamlit as st

from src.ingestion.normalizer import InputNormalizer
from src.parsing.criteria_parser import CriteriaParser
from src.scenario_expander.expander import ScenarioExpander


st.set_page_config(
    page_title="Spec2Test Intelligence",
    page_icon="🧪",
    layout="wide",
)

SAMPLE_ACCEPTANCE_CRITERIA = """1. User should be able to log in with valid username and password.
2. System should not allow login with invalid credentials.
3. Error message should be shown when required fields are blank.
4. Given the user is on the password reset page when the user enters a registered email then the reset link should be sent successfully.
"""


def initialize_session_state() -> None:
    defaults: dict[str, Any] = {
        "acceptance_criteria": "",
        "load_sample": False,
        "generated_test_cases": [],
        "parsed_acceptance_criteria": [],
        "has_generated": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def handle_sample_toggle() -> None:
    if st.session_state.load_sample:
        st.session_state.acceptance_criteria = SAMPLE_ACCEPTANCE_CRITERIA
    else:
        st.session_state.acceptance_criteria = ""


def create_excel_file(dataframe: pd.DataFrame) -> io.BytesIO:
    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Generated Test Cases",
        )

        worksheet = writer.sheets["Generated Test Cases"]

        for column_cells in worksheet.columns:
            column_letter = column_cells[0].column_letter
            maximum_length = 0

            for cell in column_cells:
                if cell.value is not None:
                    maximum_length = max(
                        maximum_length,
                        len(str(cell.value)),
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


def display_test_case_card(test_case: Any, include_preconditions: bool) -> None:
    with st.container(border=True):
        header_left, header_middle, header_right = st.columns(
            [2, 1, 1]
        )

        with header_left:
            st.markdown(f"### {test_case.test_case_id}")

        with header_middle:
            st.markdown(f"**Type:** {test_case.scenario_type}")

        with header_right:
            st.markdown(f"**Priority:** {test_case.priority}")

        st.markdown("#### Test Scenario")
        st.write(test_case.test_scenario)

        st.markdown("#### Description")
        st.write(test_case.test_case_description)

        if include_preconditions:
            st.markdown("#### Preconditions")
            for index, precondition in enumerate(
                test_case.preconditions,
                start=1,
            ):
                st.write(f"{index}. {precondition}")

        st.markdown("#### Test Steps")
        for index, step in enumerate(
            test_case.test_steps,
            start=1,
        ):
            st.write(f"{index}. {step}")

        st.markdown("#### Test Data")
        st.write(test_case.test_data or "Not specified")

        st.markdown("#### Expected Result")
        st.write(test_case.expected_result)

        st.markdown(
            f"**Requirement ID:** {test_case.requirement_id}"
        )


def build_export_dataframe(
    test_cases: list[Any],
    include_preconditions: bool,
) -> pd.DataFrame:
    table_data = []

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

        table_data.append(row)

    return pd.DataFrame(table_data)


initialize_session_state()

st.title("🧪 Spec2Test Intelligence")
st.caption(
    "Transform acceptance criteria into structured, traceable QA test cases."
)

st.checkbox(
    "Load sample acceptance criteria",
    key="load_sample",
    on_change=handle_sample_toggle,
)

st.text_area(
    "Acceptance Criteria",
    key="acceptance_criteria",
    height=220,
    placeholder=(
        "Paste acceptance criteria here.\n\n"
        "Example:\n"
        "1. User should be able to log in with valid credentials.\n"
        "2. System should reject invalid credentials."
    ),
)

include_preconditions = st.checkbox(
    "Include preconditions",
    value=True,
)

generate = st.button(
    "Generate Test Cases",
    type="primary",
)

if generate:
    input_text = st.session_state.acceptance_criteria

    if not input_text.strip():
        st.warning("Please enter acceptance criteria.")
        st.session_state.generated_test_cases = []
        st.session_state.parsed_acceptance_criteria = []
        st.session_state.has_generated = False

    else:
        try:
            normalizer = InputNormalizer()
            parser = CriteriaParser()
            expander = ScenarioExpander()

            normalized_items = normalizer.normalize(input_text)
            parsed_items = parser.parse(normalized_items)
            test_cases = expander.generate(parsed_items)

            st.session_state.generated_test_cases = test_cases
            st.session_state.parsed_acceptance_criteria = parsed_items
            st.session_state.has_generated = True

        except Exception as error:
            st.session_state.generated_test_cases = []
            st.session_state.parsed_acceptance_criteria = []
            st.session_state.has_generated = False
            st.error(f"Error: {error}")

if st.session_state.has_generated:
    test_cases = st.session_state.generated_test_cases
    parsed_items = st.session_state.parsed_acceptance_criteria

    st.success(f"Generated {len(test_cases)} test cases.")

    summary_column_1, summary_column_2, summary_column_3 = st.columns(3)

    positive_count = sum(
        test_case.scenario_type == "Positive"
        for test_case in test_cases
    )
    negative_count = sum(
        test_case.scenario_type == "Negative"
        for test_case in test_cases
    )
    edge_count = sum(
        test_case.scenario_type == "Edge"
        for test_case in test_cases
    )

    with summary_column_1:
        st.metric("Positive Cases", positive_count)

    with summary_column_2:
        st.metric("Negative Cases", negative_count)

    with summary_column_3:
        st.metric("Edge Cases", edge_count)

    st.subheader("Generated Test Cases")

    scenario_filter = st.multiselect(
        "Filter by scenario type",
        options=["Positive", "Negative", "Edge"],
        default=["Positive", "Negative", "Edge"],
        key="scenario_filter",
    )

    filtered_test_cases = [
        test_case
        for test_case in test_cases
        if test_case.scenario_type in scenario_filter
    ]

    st.caption(
        f"Showing {len(filtered_test_cases)} of "
        f"{len(test_cases)} generated test cases."
    )

    if not filtered_test_cases:
        st.info(
            "Select at least one scenario type to display test cases."
        )
    else:
        for test_case in filtered_test_cases:
            display_test_case_card(
                test_case,
                include_preconditions,
            )

    dataframe = build_export_dataframe(
        test_cases,
        include_preconditions,
    )

    json_output = json.dumps(
        [
            test_case.model_dump()
            for test_case in test_cases
        ],
        indent=2,
    )

    excel_output = create_excel_file(dataframe)

    download_column_1, download_column_2 = st.columns(2)

    with download_column_1:
        st.download_button(
            label="Download JSON",
            data=json_output,
            file_name="generated_test_cases.json",
            mime="application/json",
            use_container_width=True,
        )

    with download_column_2:
        st.download_button(
            label="Download Excel",
            data=excel_output,
            file_name="generated_test_cases.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
        )

    with st.expander("Parsed Acceptance Criteria"):
        for item in parsed_items:
            st.json(item.model_dump())