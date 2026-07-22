from typing import Any

import streamlit as st

from app.config import SUPPORTED_SCENARIO_TYPES


def show_scenario_filter(
    test_cases: list[Any],
) -> list[Any]:
    selected_scenario_types = st.multiselect(
        "Filter by scenario type",
        options=SUPPORTED_SCENARIO_TYPES,
        default=SUPPORTED_SCENARIO_TYPES,
        key="scenario_filter",
    )

    filtered_test_cases = [
        test_case
        for test_case in test_cases
        if test_case.scenario_type in selected_scenario_types
    ]

    st.caption(
        f"Showing {len(filtered_test_cases)} of "
        f"{len(test_cases)} generated test cases."
    )

    return filtered_test_cases