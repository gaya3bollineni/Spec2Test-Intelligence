import streamlit as st

from src.models.schemas import TestCase
from src.playwright.dom_parser import DOMParser
from src.playwright.generator import PlaywrightGenerator


def show_playwright_generation(
    test_cases: list[TestCase],
) -> None:
    """
    Displays Playwright generation controls,
    optional DOM upload, DOM and Shadow DOM
    analysis status, generation warnings,
    code preview, and .spec.ts download.
    """

    st.subheader("Playwright Automation")

    st.caption(
        "Convert generated Spec2Test test cases into "
        "deterministic Playwright TypeScript tests."
    )

    if not test_cases:
        st.warning(
            "Generate test cases before creating "
            "Playwright automation."
        )
        return

    st.markdown(
        "#### Optional DOM / HTML"
    )

    st.caption(
        "Upload application HTML to generate locators "
        "from actual DOM elements. Open declarative "
        "Shadow DOM is supported. If no DOM is supplied, "
        "Spec2Test continues using requirement-inferred "
        "locators."
    )

    uploaded_dom = st.file_uploader(
        "Upload application HTML",
        type=["html", "htm"],
        key="playwright_dom_upload",
        help=(
            "Optional. Upload an HTML snapshot of the "
            "application page used by these test cases. "
            "Open declarative Shadow DOM, including nested "
            "shadow roots, can be analyzed."
        ),
    )

    dom_elements = None
    shadow_dom_element_count = 0
    shadow_root_count = 0
    nested_shadow_dom = False

    if uploaded_dom is not None:
        try:
            html = uploaded_dom.getvalue().decode(
                "utf-8"
            )

            dom_result = DOMParser().parse(
                html
            )

            dom_elements = (
                dom_result.elements
            )

            shadow_dom_elements = [
                element
                for element in dom_result.elements
                if element.inside_shadow_dom
            ]

            shadow_dom_element_count = len(
                shadow_dom_elements
            )

            shadow_paths = {
                tuple(element.shadow_host_path)
                for element in shadow_dom_elements
                if element.shadow_host_path
            }

            shadow_root_count = len(
                {
                    host
                    for path in shadow_paths
                    for host in path
                }
            )

            nested_shadow_dom = any(
                len(element.shadow_host_path) > 1
                for element in shadow_dom_elements
            )

            if dom_result.elements:
                st.success(
                    "DOM analyzed successfully."
                )

                if shadow_dom_element_count:
                    st.success(
                        "Open Shadow DOM detected. "
                        f"{shadow_dom_element_count} interactive "
                        "element"
                        f"{'' if shadow_dom_element_count == 1 else 's'} "
                        "found inside "
                        f"{shadow_root_count} shadow root"
                        f"{'' if shadow_root_count == 1 else 's'}."
                    )

                    if nested_shadow_dom:
                        st.caption(
                            "Nested Shadow DOM was detected "
                            "and included in locator matching."
                        )

                metric_col, mode_col = (
                    st.columns(2)
                )

                with metric_col:
                    st.metric(
                        "Interactive Elements",
                        (
                            dom_result
                            .interactive_element_count
                        ),
                    )

                with mode_col:
                    st.metric(
                        "Locator Mode",
                        (
                            "DOM + Shadow DOM"
                            if shadow_dom_element_count
                            else "DOM-Aware"
                        ),
                    )

                if shadow_dom_element_count:
                    shadow_col, root_col = (
                        st.columns(2)
                    )

                    with shadow_col:
                        st.metric(
                            "Shadow DOM Elements",
                            shadow_dom_element_count,
                        )

                    with root_col:
                        st.metric(
                            "Open Shadow Roots",
                            shadow_root_count,
                        )

            else:
                st.warning(
                    "The uploaded HTML did not contain "
                    "supported interactive elements. "
                    "Spec2Test will use inferred locators."
                )

            if dom_result.warnings:
                with st.expander(
                    "DOM Analysis Warnings",
                    expanded=True,
                ):
                    for warning in (
                        dom_result.warnings
                    ):
                        st.markdown(
                            f"- {warning}"
                        )

        except UnicodeDecodeError:
            st.error(
                "The uploaded HTML could not be read as "
                "UTF-8 text. Please upload a valid HTML "
                "file."
            )

            dom_elements = None

        except Exception as exc:
            st.error(
                "The uploaded HTML could not be analyzed: "
                f"{exc}"
            )

            dom_elements = None

    else:
        st.info(
            "No DOM uploaded. Playwright locators will "
            "be inferred from requirement and test-step "
            "information."
        )

    st.divider()

    if st.button(
        "Generate Playwright Test",
        key="generate_playwright",
        width="stretch",
    ):
        generator = PlaywrightGenerator()

        result = generator.generate(
            test_cases,
            dom_elements=dom_elements,
        )

        st.session_state.playwright_result = (
            result
        )

        st.session_state.playwright_locator_mode = (
            "DOM + Shadow DOM"
            if shadow_dom_element_count
            else (
                "DOM-Aware"
                if dom_elements
                else "Inferred"
            )
        )

        st.session_state.playwright_dom_count = (
            len(dom_elements)
            if dom_elements
            else 0
        )

        st.session_state.playwright_shadow_dom_count = (
            shadow_dom_element_count
        )

        st.session_state.playwright_shadow_root_count = (
            shadow_root_count
        )

        st.session_state.playwright_nested_shadow_dom = (
            nested_shadow_dom
        )

    result = st.session_state.get(
        "playwright_result"
    )

    if result is None:
        return

    locator_mode = (
        st.session_state.get(
            "playwright_locator_mode",
            "Inferred",
        )
    )

    dom_count = (
        st.session_state.get(
            "playwright_dom_count",
            0,
        )
    )

    generated_shadow_count = (
        st.session_state.get(
            "playwright_shadow_dom_count",
            0,
        )
    )

    generated_shadow_root_count = (
        st.session_state.get(
            "playwright_shadow_root_count",
            0,
        )
    )

    generated_nested_shadow_dom = (
        st.session_state.get(
            "playwright_nested_shadow_dom",
            False,
        )
    )

    st.divider()

    st.success(
        f"Generated {result.generated_test_count} "
        "Playwright test"
        f"{'' if result.generated_test_count == 1 else 's'}."
    )

    if locator_mode == "DOM + Shadow DOM":
        st.info(
            "Generation mode: DOM + Shadow DOM. "
            f"{dom_count} interactive DOM element"
            f"{'' if dom_count == 1 else 's'} "
            "were available for locator matching, including "
            f"{generated_shadow_count} element"
            f"{'' if generated_shadow_count == 1 else 's'} "
            "inside "
            f"{generated_shadow_root_count} open shadow root"
            f"{'' if generated_shadow_root_count == 1 else 's'}."
        )

        if generated_nested_shadow_dom:
            st.caption(
                "Nested Shadow DOM was included in this "
                "generation."
            )

    elif locator_mode == "DOM-Aware":
        st.info(
            "Generation mode: DOM-Aware. "
            f"{dom_count} interactive DOM element"
            f"{'' if dom_count == 1 else 's'} "
            "were available for locator matching."
        )

    else:
        st.info(
            "Generation mode: Inferred. "
            "No usable DOM was supplied, so locators "
            "were inferred from requirement and "
            "test-step information."
        )

    test_col, warning_col, mode_col = (
        st.columns(3)
    )

    with test_col:
        st.metric(
            "Playwright Tests",
            result.generated_test_count,
        )

    with warning_col:
        st.metric(
            "Review Warnings",
            len(result.warnings),
        )

    with mode_col:
        st.metric(
            "Locator Mode",
            locator_mode,
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