import streamlit as st

from src.models.schemas import TestCase
from src.playwright.generator import PlaywrightGenerator


def show_playwright_generation(
    test_cases: list[TestCase],
) -> None:
    """
    Displays Playwright generation controls, code preview,
    warnings, and .spec.ts download.
    """

    st.subheader("Playwright Automation")

    st.caption(
        "Convert generated Spec2Test test cases into "
        "deterministic Playwright TypeScript tests."
    )

    st.info(
        "Generated locators are based on requirement and test-step "
        "information. Spec2Test does not inspect the live application's "
        "DOM, so locators and assertions should be reviewed before "
        "running the generated automation."
    )

    if not test_cases:
        st.warning(
            "Generate test cases before creating "
            "Playwright automation."
        )
        return

    if st.button(
        "Generate Playwright Test",
        key="generate_playwright",
    ):
        generator = PlaywrightGenerator()

        result = generator.generate(
            test_cases
        )

        st.session_state.playwright_result = result

    result = st.session_state.get(
        "playwright_result"
    )

    if result is None:
        return

    metric_col, warning_col = st.columns(2)

    with metric_col:
        st.metric(
            "Playwright Tests",
            result.generated_test_count,
        )

    with warning_col:
        st.metric(
            "Review Warnings",
            len(result.warnings),
        )

    if result.warnings:
        with st.expander(
            "Generation Warnings",
            expanded=False,
        ):
            for warning in result.warnings:
                st.warning(warning)

    st.markdown("#### TypeScript Preview")

    st.code(
        result.typescript_code,
        language="typescript",
    )

    st.download_button(
        label="Download Playwright Test (.spec.ts)",
        data=result.typescript_code,
        file_name="spec2test.generated.spec.ts",
        mime="text/plain",
        key="download_playwright",
    )