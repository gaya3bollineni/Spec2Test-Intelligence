import io
import json

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

st.title("🧪 Spec2Test Intelligence")
st.caption(
    "Transform acceptance criteria into structured, traceable QA test cases."
)


SAMPLE_ACCEPTANCE_CRITERIA = """1. User should be able to log in with valid username and password.
2. System should not allow login with invalid credentials.
3. Error message should be shown when required fields are blank.
4. Given the user is on the password reset page when the user enters a registered email then the reset link should be sent successfully.
"""


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


def display_test_case_card(test_case, include_preconditions: bool) -> None:
    scenario_type = test_case.scenario_type
    priority = test_case.priority

    st.markdown(
        f"""
        <div style="
            border: 1px solid #d0d5dd;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 14px;
            background-color: #ffffff;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            ">
                <div>
                    <span style="
                        font-size: 18px;
                        font-weight: 700;
                    ">
                        {test_case.test_case_id}
                    </span>
                    <span style="
                        margin-left: 10px;
                        padding: 4px 10px;
                        border-radius: 12px;
                        background-color: #f2f4f7;
                        font-size: 12px;
                    ">
                        {scenario_type}
                    </span>
                </div>

                <span style="
                    padding: 4px 10px;
                    border-radius: 12px;
                    background-color: #f2f4f7;
                    font-size: 12px;
                ">
                    Priority: {priority}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Test Scenario")
    st.write(test_case.test_scenario)

    st.markdown("#### Description")
    st.write(test_case.test_case_description)

    if include_preconditions:
        st.markdown("#### Preconditions")
        for precondition in test_case.preconditions:
            st.markdown(f"- {precondition}")

    st.markdown("#### Test Steps")
    for index, step in enumerate(test_case.test_steps, start=1):
        st.markdown(f"{index}. {step}")

    st.markdown("#### Test Data")
    st.write(test_case.test_data or "Not specified")

    st.markdown("#### Expected Result")
    st.write(test_case.expected_result)

    st.markdown(
        f"**Requirement ID:** {test_case.requirement_id}"
    )

    st.divider()


load_sample = st.checkbox(
    "Load sample acceptance criteria",
    value=False,
)

input_value = (
    SAMPLE_ACCEPTANCE_CRITERIA
    if load_sample
    else ""
)

input_text = st.text_area(
    "Acceptance Criteria",
    value=input_value,
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
    if not input_text.strip():
        st.warning("Please enter acceptance criteria.")

    else:
        try:
            normalizer = InputNormalizer()
            parser = CriteriaParser()
            expander = ScenarioExpander()

            normalized_items = normalizer.normalize(input_text)
            parsed_items = parser.parse(normalized_items)
            test_cases = expander.generate(parsed_items)

            st.success(
                f"Generated {len(test_cases)} test cases."
            )

            summary_column_1, summary_column_2, summary_column_3 = st.columns(3)

            positive_count = sum(
                1
                for test_case in test_cases
                if test_case.scenario_type == "Positive"
            )

            negative_count = sum(
                1
                for test_case in test_cases
                if test_case.scenario_type == "Negative"
            )

            edge_count = sum(
                1
                for test_case in test_cases
                if test_case.scenario_type == "Edge"
            )

            with summary_column_1:
                st.metric(
                    "Positive Cases",
                    positive_count,
                )

            with summary_column_2:
                st.metric(
                    "Negative Cases",
                    negative_count,
                )

            with summary_column_3:
                st.metric(
                    "Edge Cases",
                    edge_count,
                )

            st.subheader("Generated Test Cases")

            scenario_filter = st.multiselect(
                "Filter by scenario type",
                options=["Positive", "Negative", "Edge"],
                default=["Positive", "Negative", "Edge"],
            )

            filtered_test_cases = [
                test_case
                for test_case in test_cases
                if test_case.scenario_type in scenario_filter
            ]

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

            dataframe = pd.DataFrame(table_data)

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

        except Exception as error:
            st.error(f"Error: {error}")
