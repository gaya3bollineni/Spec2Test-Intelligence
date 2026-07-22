from typing import Any

import streamlit as st


def show_test_case_card(
    test_case: Any,
    include_preconditions: bool,
) -> None:
    with st.container(border=True):
        header_left, header_middle, header_right = st.columns([2, 1, 1])

        with header_left:
            st.markdown(f"### {test_case.test_case_id}")

        with header_middle:
            st.markdown(
                f"**Type:** {test_case.scenario_type}"
            )

        with header_right:
            st.markdown(
                f"**Priority:** {test_case.priority}"
            )

        st.markdown("#### Test Scenario")
        st.write(test_case.test_scenario)

        st.markdown("#### Description")
        st.write(test_case.test_case_description)

        if include_preconditions:
            st.markdown("#### Preconditions")

            for index, precondition in enumerate(
                test_case.preconditions,
                start=1,
            ):
                st.write(f"{index}. {precondition}")

        st.markdown("#### Test Steps")

        for index, step in enumerate(
            test_case.test_steps,
            start=1,
        ):
            st.write(f"{index}. {step}")

        st.markdown("#### Test Data")
        st.write(
            test_case.test_data or "Not specified"
        )

        st.markdown("#### Expected Result")
        st.write(test_case.expected_result)

        st.markdown(
            f"**Requirement ID:** {test_case.requirement_id}"
        )


def show_test_case_cards(
    test_cases: list[Any],
    include_preconditions: bool,
) -> None:
    if not test_cases:
        st.info(
            "No test cases match the selected scenario types."
        )
        return

    for test_case in test_cases:
        show_test_case_card(
            test_case=test_case,
            include_preconditions=include_preconditions,
        )