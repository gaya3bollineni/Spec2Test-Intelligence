import streamlit as st

from src.models.schemas import TestCase
from src.playwright.generator import PlaywrightGenerator


def show_playwright_generation(
    test_cases: list[TestCase],
) -> None:
    """
    Displays Playwright generation controls,
    generation status, warnings, code preview,
    and .spec.ts download.
    """

    st.subheader("Playwright Automation")

    st.caption(
        "Convert generated Spec2Test test cases into "
        "deterministic Playwright TypeScript tests."
    )

    st.info(
        "Locators are inferred from requirement and test-step "
        "information. Spec2Test does not currently inspect the "
        "application DOM, so generated locators and assertions "
        "should be reviewed before execution."
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
        width="stretch",
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

    st.divider()

    st.success(
        f"Generated {result.generated_test_count} "
        "Playwright test"
        f"{'' if result.generated_test_count == 1 else 's'}."
    )

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
        st.warning(
            f"{len(result.warnings)} generated item"
            f"{'' if len(result.warnings) == 1 else 's'} "
            "require review before running the automation."
        )

        with st.expander(
            "Review Generation Warnings",
            expanded=True,
        ):
            for warning in result.warnings:
                st.markdown(
                    f"- {warning}"
                )

    else:
        st.success(
            "No generation warnings were detected."
        )

    st.markdown(
        "#### Generated TypeScript"
    )

    st.code(
        result.typescript_code,
        language="typescript",
    )

    st.caption(
        "Download the generated Playwright tests as a "
        "TypeScript spec file. Review application-specific "
        "locators, test data, and assertions before execution."
    )

    st.download_button(
        label="Download Playwright .spec.ts",
        data=result.typescript_code,
        file_name="spec2test.generated.spec.ts",
        mime="text/plain",
        key="download_playwright",
        width="stretch",
    )