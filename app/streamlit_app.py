import io
import json
import pandas as pd
import streamlit as st

from src.ingestion.normalizer import InputNormalizer
from src.parsing.criteria_parser import CriteriaParser
from src.scenario_expander.expander import ScenarioExpander


st.set_page_config(page_title="Spec2Test Intelligence", layout="wide")

st.title("Spec2Test Intelligence")
st.caption("Transform acceptance criteria into structured QA test cases.")

default_text = """1. User should be able to log in with valid username and password.
2. System should not allow login with invalid credentials.
3. Error message should be shown when required fields are blank.
4. Given the user is on the password reset page when the user enters a registered email then the reset link should be sent successfully.
"""

input_text = st.text_area(
    "Paste acceptance criteria",
    value=default_text,
    height=220,
)

generate = st.button("Generate Test Cases", type="primary")

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

            st.success(f"Generated {len(test_cases)} test cases.")

            table_data = []
            for tc in test_cases:
                table_data.append({
                     "Test Case ID": tc.test_case_id,
                     "Requirement ID": tc.requirement_id,
                     "Scenario Type": tc.scenario_type,
                     "Test Scenario": tc.test_scenario,
                     "Description": tc.test_case_description,
                     "Preconditions": "\n".join(tc.preconditions),
                     "Steps": "\n".join([f"{i + 1}. {step}" for i, step in enumerate(tc.test_steps)]),
                     "Test Data": tc.test_data,
                     "Expected Result": tc.expected_result,
                     "Priority": tc.priority,
                })

            df = pd.DataFrame(table_data)

            st.subheader("Generated Test Cases")
            st.dataframe(df, use_container_width=True)

            json_str = json.dumps([tc.model_dump() for tc in test_cases], indent=2)

            excel_buffer = io.BytesIO()
            export_df = df
                '''columns={
                    "test_case_id": "Test Case ID",
                    "title": "Title",
                    "scenario": "Scenario",
                    "preconditions": "Preconditions",
                    "test_steps": "Steps",
                    "expected_result": "Expected Result",
                    "priority": "Priority",
                    "test_type": "Type",
                    "source_criterion_id": "Source AC",
                } '''
            
            export_df.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name="generated_test_cases.json",
                    mime="application/json",
                    use_container_width=True,
                )

            with col2:
                st.download_button(
                    label="Download Excel",
                    data=excel_buffer,
                    file_name="generated_test_cases.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            with st.expander("Parsed Acceptance Criteria"):
                for item in parsed_items:
                    st.json(item.model_dump())

        except Exception as e:
            st.error(f"Error: {str(e)}")