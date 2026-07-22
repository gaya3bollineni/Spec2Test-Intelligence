from typing import Any

import streamlit as st

from app.config import SAMPLE_ACCEPTANCE_CRITERIA


SESSION_DEFAULTS: dict[str, Any] = {
    "acceptance_criteria": "",
    "load_sample": False,
    "include_preconditions": True,
    "generated_test_cases": [],
    "parsed_acceptance_criteria": [],
    "requirement_analysis": None,
    "completeness_analysis": None,
    "has_generated": False,
}


def initialize_session_state() -> None:
    for key, default_value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def handle_sample_toggle() -> None:
    st.session_state.acceptance_criteria = (
        SAMPLE_ACCEPTANCE_CRITERIA
        if st.session_state.load_sample
        else ""
    )


def clear_generated_results() -> None:
    st.session_state.generated_test_cases = []
    st.session_state.parsed_acceptance_criteria = []
    st.session_state.requirement_analysis = None
    st.session_state.completeness_analysis = None
    st.session_state.has_generated = False


def save_generated_results(
    test_cases: list[Any],
    parsed_items: list[Any],
    requirement_analysis: Any,
    completeness_analysis: Any,
) -> None:
    st.session_state.generated_test_cases = test_cases
    st.session_state.parsed_acceptance_criteria = parsed_items
    st.session_state.requirement_analysis = requirement_analysis
    st.session_state.completeness_analysis = completeness_analysis
    st.session_state.has_generated = True