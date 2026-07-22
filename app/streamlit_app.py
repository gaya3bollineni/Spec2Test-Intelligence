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
from app.ui.testcase_cards import show_test_case_cards


st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
)


def show_input_section() -> bool:
    """
    Displays the input controls and returns True when
    the Generate Test Cases button is clicked.
    """

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

    st.checkbox(
        "Include preconditions",
        key="include_preconditions",
        value=True,
    )

    return st.button(
        "Generate Test Cases",
        type="primary",
    )


def generate_results() -> None:
    """
    Processes the acceptance criteria and stores the generated
    results in Streamlit session state.
    """

    acceptance_criteria = st.session_state.acceptance_criteria

    if not acceptance_criteria.strip():
        clear_generated_results()
        st.warning("Please enter acceptance criteria.")
        return

    try:
        (
            test_cases,
            parsed_items,
            requirement_analysis,
            completeness_analysis,
        ) = generate_spec2test_results(
            acceptance_criteria
        )

        save_generated_results(
            test_cases=test_cases,
            parsed_items=parsed_items,
            requirement_analysis=requirement_analysis,
            completeness_analysis=completeness_analysis,
        )

    except Exception as error:
        clear_generated_results()
        st.error(
            f"Unable to generate test cases: {error}"
        )


def show_generated_results() -> None:
    """
    Displays requirement analysis, test case summaries,
    generated test cases, filters, and export buttons.
    """

    test_cases = st.session_state.generated_test_cases
    parsed_items = st.session_state.parsed_acceptance_criteria
    requirement_analysis = st.session_state.requirement_analysis
    completeness_analysis = st.session_state.completeness_analysis
    include_preconditions = st.session_state.include_preconditions

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

    st.subheader("Generated Test Cases")

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
    )

    show_parsed_acceptance_criteria(
        parsed_items=parsed_items,
    )


def main() -> None:
    initialize_session_state()

    st.title(
        f"{APP_ICON} {APP_NAME}"
    )
    st.caption(
        APP_DESCRIPTION
    )

    generate_button_clicked = show_input_section()

    if generate_button_clicked:
        generate_results()

    if st.session_state.has_generated:
        show_generated_results()


if __name__ == "__main__":
    main()