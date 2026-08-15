from typing import Any

import streamlit as st


def show_requirement_warnings(
    requirement_analysis: Any,
) -> None:
    if requirement_analysis.warnings:
        with st.expander(
            "Requirement Warnings",
            expanded=True,
        ):
            for warning in requirement_analysis.warnings:
                st.warning(
                    f"{warning.criterion_id}: "
                    f"{warning.message}"
                )

                st.write(
                    "Recommendation: "
                    f"{warning.recommendation}"
                )

    else:
        st.success(
            "No ambiguous wording was detected."
        )


def show_duplicate_requirements(
    duplicate_requirements: list[Any],
) -> None:
    if not duplicate_requirements:
        st.success(
            "No duplicate requirements were detected."
        )
        return

    with st.expander(
        "Duplicate Requirements",
        expanded=True,
    ):
        for duplicate in duplicate_requirements:
            st.warning(
                f"{duplicate.requirement_id} duplicates "
                f"{duplicate.duplicate_of}"
            )

            st.write(
                f"Duplicate: "
                f"{duplicate.requirement_text}"
            )

            st.write(
                f"Original: "
                f"{duplicate.duplicate_text}"
            )


def show_conflicting_requirements(
    conflicting_requirements: list[Any],
) -> None:
    if not conflicting_requirements:
        st.success(
            "No direct requirement conflicts were detected."
        )
        return

    with st.expander(
        "Conflicting Requirements",
        expanded=True,
    ):
        for conflict in conflicting_requirements:
            st.error(
                f"{conflict.requirement_id} conflicts with "
                f"{conflict.conflicts_with}"
            )

            st.write(
                f"Requirement: "
                f"{conflict.requirement_text}"
            )

            st.write(
                f"Conflicting Requirement: "
                f"{conflict.conflicting_text}"
            )

            st.write(
                f"Reason: {conflict.reason}"
            )


def show_completeness_details(
    completeness_analysis: Any,
) -> None:
    with st.expander(
        "Requirement Completeness Details",
        expanded=True,
    ):
        for criterion_result in (
            completeness_analysis.criterion_results
        ):
            st.markdown(
                f"### {criterion_result.criterion_id} — "
                f"{criterion_result.completeness_score}%"
            )

            st.write(
                criterion_result.criterion_text
            )

            for check in criterion_result.checks:
                if check.is_present:
                    st.success(
                        f"✓ {check.message}"
                    )

                else:
                    st.warning(
                        f"⚠ {check.message}"
                    )

            if criterion_result.recommendations:
                st.markdown(
                    "**Recommendations**"
                )

                for recommendation in (
                    criterion_result.recommendations
                ):
                    st.write(
                        f"- {recommendation}"
                    )

            st.divider()


def show_parsed_acceptance_criteria(
    parsed_items: list[Any],
) -> None:
    with st.expander(
        "Parsed Acceptance Criteria"
    ):
        for item in parsed_items:
            st.json(
                item.model_dump()
            )

def show_requirement_dependencies(
    dependencies: list[Any],
) -> None:
    if not dependencies:
        st.success(
            "No obvious requirement dependencies were detected."
        )
        return

    with st.expander(
        "Potential Requirement Dependencies",
        expanded=True,
    ):
        for dependency in dependencies:
            st.info(
                f"{dependency.requirement_id} may depend on "
                f"{dependency.depends_on}"
            )

            st.write(
                f"Requirement: {dependency.requirement_text}"
            )

            st.write(
                f"Depends on: {dependency.dependency_text}"
            )

            st.write(
                f"Reason: {dependency.reason}"
            )  
def show_requirement_health(
    health_scores: list[Any],
) -> None:

    st.subheader("Requirement Health")

    if not health_scores:
        st.info(
            "Requirement health information is not available."
        )
        return

    overall_average = round(
        sum(
            health.overall_score
            for health in health_scores
        )
        / len(health_scores)
    )

    st.metric(
        "Overall Requirement Health",
        f"{overall_average}/100",
    )

    for health in health_scores:
        with st.expander(
            (
                f"{health.requirement_id} — "
                f"{health.overall_score}/100 "
                f"({health.rating})"
            )
        ):
            st.write(
                health.requirement_text
            )

            column1, column2, column3 = st.columns(3)

            column1.metric(
                "Completeness",
                f"{health.completeness_score}/100",
            )

            column2.metric(
                "Clarity",
                f"{health.clarity_score}/100",
            )

            column3.metric(
                "Uniqueness",
                f"{health.uniqueness_score}/100",
            )

            column4, column5 = st.columns(2)

            column4.metric(
                "Consistency",
                f"{health.consistency_score}/100",
            )

            column5.metric(
                "Dependency",
                f"{health.dependency_score}/100",
            )

            if health.deductions:
                st.markdown(
                    "**Why points were deducted**"
                )

                for deduction in health.deductions:
                    st.write(
                        f"- {deduction}"
                    )

            else:
                st.success(
                    "No quality deductions were detected."
                )          