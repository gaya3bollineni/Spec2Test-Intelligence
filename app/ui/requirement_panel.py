from typing import Any

import streamlit as st


def show_requirement_warnings(requirement_analysis: Any) -> None:
    if requirement_analysis.warnings:
        with st.expander(
            "Requirement Warnings",
            expanded=True,
        ):
            for warning in requirement_analysis.warnings:
                st.warning(
                    f"{warning.criterion_id}: {warning.message}"
                )

                st.write(
                    f"Recommendation: {warning.recommendation}"
                )
    else:
        st.success(
            "No ambiguous wording was detected in the acceptance criteria."
        )


def show_completeness_details(
    completeness_analysis: Any,
) -> None:
    with st.expander(
        "Requirement Completeness Details",
        expanded=True,
    ):
        for criterion_result in completeness_analysis.criterion_results:
            st.markdown(
                f"### {criterion_result.criterion_id} — "
                f"{criterion_result.completeness_score}%"
            )

            st.write(criterion_result.criterion_text)

            for check in criterion_result.checks:
                if check.is_present:
                    st.success(f"✓ {check.message}")
                else:
                    st.warning(f"⚠ {check.message}")

            if criterion_result.recommendations:
                st.markdown("**Recommendations**")

                for recommendation in criterion_result.recommendations:
                    st.write(f"- {recommendation}")

            st.divider()


def show_parsed_acceptance_criteria(
    parsed_items: list[Any],
) -> None:
    with st.expander("Parsed Acceptance Criteria"):
        for item in parsed_items:
            st.json(item.model_dump())