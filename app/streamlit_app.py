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
from app.ui.data_testing import show_data_testing
from app.ui.requirement_panel import (
    show_completeness_details,
    show_conflicting_requirements,
    show_duplicate_requirements,
    show_parsed_acceptance_criteria,
    show_requirement_dependencies,
    show_requirement_warnings,
    show_requirement_health,
)
from app.ui.exports import show_export_buttons
from app.ui.filters import show_scenario_filter
from app.ui.helpers import generate_spec2test_results
from app.ui.requirement_panel import (
    show_completeness_details,
    show_conflicting_requirements,
    show_duplicate_requirements,
    show_parsed_acceptance_criteria,
    show_requirement_warnings,
)
from app.ui.session import (
    clear_generated_results,
    handle_sample_toggle,
    initialize_session_state,
    save_generated_results,
)
from app.ui.templates import (
    build_requirements_template,
)
from app.ui.testcase_cards import (
    show_test_case_cards,
)
from app.ui.traceability import (
    show_traceability_matrix,
)
from src.ingestion.excel_loader import (
    ExcelRequirementLoader,
)


st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
)


def clear_manual_input() -> None:
    st.session_state.excel_requirement_records = []


def load_excel_requirements(
    uploaded_file,
) -> None:
    try:
        loader = ExcelRequirementLoader()

        dataframe = loader.load(
            uploaded_file
        )

        requirement_records = loader.to_records(
            dataframe
        )

        st.session_state.excel_requirement_records = (
            requirement_records
        )

        st.session_state.acceptance_criteria = (
            loader.to_text(
                dataframe
            )
        )

        st.session_state.load_sample = False

        st.success(
            f"Loaded {len(dataframe)} requirements "
            "from Excel."
        )

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True,
        )

    except ValueError as error:
        st.session_state.acceptance_criteria = ""
        st.session_state.excel_requirement_records = []

        clear_generated_results()

        st.error(
            str(error)
        )

    except Exception as error:
        st.session_state.acceptance_criteria = ""
        st.session_state.excel_requirement_records = []

        clear_generated_results()

        st.error(
            "Unable to process the uploaded Excel file: "
            f"{error}"
        )


def show_manual_input() -> None:
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
    st.download_button(
        label="Download Requirements Template",
        data=build_requirements_template(),
        file_name=(
            "spec2test_requirements_template.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    uploaded_file = st.file_uploader(
        "Upload Requirements Excel",
        type=["xlsx"],
        help=(
            "Acceptance Criteria is required. "
            "Requirement ID and Priority are optional."
        ),
        key="requirements_excel_upload",
    )

    if uploaded_file is not None:
        load_excel_requirements(
            uploaded_file
        )


def show_input_section() -> bool:
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
    try:
        if (
            st.session_state.input_method
            == "Upload Excel file"
        ):
            requirement_records = (
                st.session_state.excel_requirement_records
            )

            if not requirement_records:
                clear_generated_results()

                st.warning(
                    "Please upload a valid Excel file."
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


        save_generated_results(
            test_cases=results.test_cases,
            parsed_items=results.parsed_items,
            requirement_analysis=results.requirement_analysis,
            completeness_analysis=results.completeness_analysis,
            traceability_rows=results.traceability_rows,
            duplicate_requirements=results.duplicate_requirements,
            conflicting_requirements=results.conflicting_requirements,
            dependencies=results.dependencies,
            health_scores=results.health_scores,
        )

    except Exception as error:
        clear_generated_results()

        st.error(
            f"Unable to generate test cases: {error}"
        )


def show_generated_results() -> None:
    test_cases = (
        st.session_state.generated_test_cases
    )

    parsed_items = (
        st.session_state.parsed_acceptance_criteria
    )
    dependencies = st.session_state.dependencies

    requirement_analysis = (
        st.session_state.requirement_analysis
    )

    completeness_analysis = (
        st.session_state.completeness_analysis
    )

    duplicate_requirements = (
        st.session_state.duplicate_requirements
    )

    conflicting_requirements = (
        st.session_state.conflicting_requirements
    )

    traceability_rows = (
        st.session_state.traceability_rows
    )

    include_preconditions = (
        st.session_state.include_preconditions
    )

    st.success(
        f"Generated {len(test_cases)} test cases."
    )
    health_scores = (
    st.session_state.health_scores
    )

    show_requirement_dashboard(
        requirement_analysis=requirement_analysis,
        completeness_analysis=completeness_analysis,
    )

    show_requirement_warnings(
        requirement_analysis
    )

    show_duplicate_requirements(
        duplicate_requirements
    )

    show_conflicting_requirements(
        conflicting_requirements
    )
    show_requirement_dependencies(
        dependencies
    )
    show_requirement_health(
        health_scores
    )

    show_completeness_details(
        completeness_analysis
    )

    show_test_case_summary(
        test_cases
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
        parsed_items
    )
    


def main() -> None:
    initialize_session_state()

    st.title(
        f"{APP_ICON} {APP_NAME}"
    )

    st.caption(
        APP_DESCRIPTION
    )

    requirement_tab, data_tab = st.tabs(
        [
            "Requirement Testing",
            "Data Testing",
        ]
    )

    with requirement_tab:
        generate_clicked = (
            show_input_section()
        )

        if generate_clicked:
            generate_results()

        if st.session_state.has_generated:
            show_generated_results()

    with data_tab:
        show_data_testing()


if __name__ == "__main__":
    main()