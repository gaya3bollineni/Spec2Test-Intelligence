import streamlit as st

from app.config import (
    ACCEPTANCE_CRITERIA_PLACEHOLDER,
    APP_DESCRIPTION,
    APP_ICON,
    APP_NAME,
)
from app.ui.dashboard import (
    show_requirement_dashboard,
    show_test_case_summary,
)
from app.ui.exports import show_export_buttons
from app.ui.filters import show_scenario_filter
from app.ui.helpers import generate_spec2test_results
from app.ui.requirement_panel import (
    show_completeness_details,
    show_parsed_acceptance_criteria,
    show_requirement_warnings,
)
from app.ui.session import (
    clear_generated_results,
    handle_sample_toggle,
    initialize_session_state,
    save_generated_results,
)
from app.ui.templates import build_requirements_template
from app.ui.testcase_cards import show_test_case_cards
from app.ui.traceability import show_traceability_matrix
from src.ingestion.excel_loader import ExcelRequirementLoader


st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
)


def clear_manual_input() -> None:
    """
    Clears Excel-specific state when manual input is selected.
    """

    st.session_state.excel_requirement_records = []


def load_excel_requirements(
    uploaded_file,
) -> None:
    """
    Loads structured requirements from Excel and stores both
    the records and display text in Streamlit session state.
    """

    try:
        loader = ExcelRequirementLoader()

        requirements_dataframe = loader.load(
            uploaded_file
        )

        requirement_records = loader.to_records(
            requirements_dataframe
        )

        st.session_state.excel_requirement_records = (
            requirement_records
        )

        st.session_state.acceptance_criteria = (
            loader.to_text(
                requirements_dataframe
            )
        )

        st.session_state.load_sample = False

        st.success(
            f"Loaded {len(requirements_dataframe)} "
            "requirements from Excel."
        )

        st.dataframe(
            requirements_dataframe,
            use_container_width=True,
            hide_index=True,
        )

    except ValueError as error:
        st.session_state.acceptance_criteria = ""
        st.session_state.excel_requirement_records = []
        clear_generated_results()
        st.error(str(error))

    except Exception as error:
        st.session_state.acceptance_criteria = ""
        st.session_state.excel_requirement_records = []
        clear_generated_results()

        st.error(
            f"Unable to process the uploaded Excel file: {error}"
        )


def show_manual_input() -> None:
    """
    Displays controls for manually entering acceptance criteria.
    """

    clear_manual_input()

    st.checkbox(
        "Load sample acceptance criteria",
        key="load_sample",
        on_change=handle_sample_toggle,
    )

    st.text_area(
        "Acceptance Criteria",
        key="acceptance_criteria",
        height=220,
        placeholder=ACCEPTANCE_CRITERIA_PLACEHOLDER,
    )


def show_excel_input() -> None:
    """
    Displays Excel template download and requirement upload controls.
    """

    st.download_button(
        label="Download Requirements Template",
        data=build_requirements_template(),
        file_name="spec2test_requirements_template.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    uploaded_file = st.file_uploader(
        "Upload Requirements Excel",
        type=["xlsx"],
        help=(
            "The workbook must contain an Acceptance Criteria "
            "column. Requirement ID and Priority are optional."
        ),
        key="requirements_excel_upload",
    )

    if uploaded_file is not None:
        load_excel_requirements(
            uploaded_file
        )


def show_input_section() -> bool:
    """
    Displays the requirement input controls and returns True
    when the Generate Test Cases button is clicked.
    """

    input_method = st.radio(
        "Choose requirement input method",
        options=[
            "Enter acceptance criteria",
            "Upload Excel file",
        ],
        horizontal=True,
        key="input_method",
    )

    if input_method == "Enter acceptance criteria":
        show_manual_input()
    else:
        show_excel_input()

    st.checkbox(
        "Include preconditions",
        key="include_preconditions",
    )

    return st.button(
        "Generate Test Cases",
        type="primary",
    )


def generate_results() -> None:
    """
    Processes either manual text or structured Excel records and
    stores the generated results in Streamlit session state.
    """

    try:
        if st.session_state.input_method == "Upload Excel file":
            requirement_records = (
                st.session_state.excel_requirement_records
            )

            if not requirement_records:
                clear_generated_results()

                st.warning(
                    "Please upload an Excel file containing "
                    "valid acceptance criteria."
                )
                return

            results = generate_spec2test_results(
                requirement_records=requirement_records
            )

        else:
            acceptance_criteria = (
                st.session_state.acceptance_criteria
            )

            if not acceptance_criteria.strip():
                clear_generated_results()

                st.warning(
                    "Please enter acceptance criteria."
                )
                return

            results = generate_spec2test_results(
                acceptance_criteria=acceptance_criteria
            )

        (
            test_cases,
            parsed_items,
            requirement_analysis,
            completeness_analysis,
            traceability_rows,
        ) = results

        save_generated_results(
            test_cases=test_cases,
            parsed_items=parsed_items,
            requirement_analysis=requirement_analysis,
            completeness_analysis=completeness_analysis,
            traceability_rows=traceability_rows,
        )

    except Exception as error:
        clear_generated_results()

        st.error(
            f"Unable to generate test cases: {error}"
        )


def show_generated_results() -> None:
    """
    Displays requirement analysis, traceability, generated test
    cases, filters, and export controls.
    """

    test_cases = (
        st.session_state.generated_test_cases
    )

    parsed_items = (
        st.session_state.parsed_acceptance_criteria
    )

    requirement_analysis = (
        st.session_state.requirement_analysis
    )

    completeness_analysis = (
        st.session_state.completeness_analysis
    )

    include_preconditions = (
        st.session_state.include_preconditions
    )

    traceability_rows = (
        st.session_state.traceability_rows
    )

    st.success(
        f"Generated {len(test_cases)} test cases."
    )

    show_requirement_dashboard(
        requirement_analysis=requirement_analysis,
        completeness_analysis=completeness_analysis,
    )

    show_requirement_warnings(
        requirement_analysis=requirement_analysis,
    )

    show_completeness_details(
        completeness_analysis=completeness_analysis,
    )

    show_test_case_summary(
        test_cases=test_cases,
    )

    show_traceability_matrix(
        traceability_rows
    )

    st.subheader(
        "Generated Test Cases"
    )

    filtered_test_cases = show_scenario_filter(
        test_cases=test_cases,
    )

    show_test_case_cards(
        test_cases=filtered_test_cases,
        include_preconditions=include_preconditions,
    )

    show_export_buttons(
        test_cases=test_cases,
        include_preconditions=include_preconditions,
        traceability_rows=traceability_rows,
    )

    show_parsed_acceptance_criteria(
        parsed_items=parsed_items,
    )


def main() -> None:
    """
    Runs the Spec2Test Intelligence application.
    """

    initialize_session_state()

    st.title(
        f"{APP_ICON} {APP_NAME}"
    )

    st.caption(
        APP_DESCRIPTION
    )

    generate_button_clicked = (
        show_input_section()
    )

    if generate_button_clicked:
        generate_results()

    if st.session_state.has_generated:
        show_generated_results()


if __name__ == "__main__":
    main()