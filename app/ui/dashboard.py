from typing import Any

import streamlit as st


def show_requirement_dashboard(
    requirement_analysis: Any,
    completeness_analysis: Any,
) -> None:
    st.subheader("Requirement Intelligence")

    (
        column_1,
        column_2,
        column_3,
        column_4,
    ) = st.columns(4)

    with column_1:
        st.metric(
            "Acceptance Criteria",
            requirement_analysis.total_criteria,
        )

    with column_2:
        st.metric(
            "Requirement Quality",
            f"{requirement_analysis.quality_score}%",
        )

    with column_3:
        st.metric(
            "Completeness",
            f"{completeness_analysis.overall_score}%",
        )

    with column_4:
        st.metric(
            "Ambiguous Criteria",
            requirement_analysis.ambiguous_criteria_count,
        )


def show_test_case_summary(test_cases: list[Any]) -> None:
    st.subheader("Test Case Summary")

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

    column_1, column_2, column_3 = st.columns(3)

    with column_1:
        st.metric(
            "Positive Cases",
            positive_count,
        )

    with column_2:
        st.metric(
            "Negative Cases",
            negative_count,
        )

    with column_3:
        st.metric(
            "Edge Cases",
            edge_count,
        )