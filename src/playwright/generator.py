from typing import List

from src.models.schemas import TestCase
from src.playwright.action_mapper import (
    PlaywrightActionMapper,
)
from src.playwright.intent import (
    AutomationAssertion,
    AutomationIntent,
    AutomationIntentExtractor,
)
from src.playwright.models import (
    PlaywrightAction,
    PlaywrightGenerationResult,
    PlaywrightLocator,
    PlaywrightTest,
)


class PlaywrightGenerator:
    """
    Converts Spec2Test TestCase objects into
    deterministic Playwright TypeScript tests.

    Application-specific behavior is left as TODO
    rather than fabricating unreliable assertions.
    """

    def __init__(self) -> None:
        self.action_mapper = (
            PlaywrightActionMapper()
        )

        self.intent_extractor = (
            AutomationIntentExtractor()
        )

    def generate(
        self,
        test_cases: List[TestCase],
    ) -> PlaywrightGenerationResult:
        playwright_tests: list[
            PlaywrightTest
        ] = []

        warnings: list[str] = []

        intents: dict[
            str,
            AutomationIntent,
        ] = {}

        for test_case in test_cases:
            intent = (
                self.intent_extractor.extract(
                    test_case
                )
            )

            intents[
                test_case.test_case_id
            ] = intent

            actions = (
                self.action_mapper.map_intent(
                    intent
                )
            )

            if len(actions) <= 1:
                warnings.append(
                    (
                        f"{test_case.test_case_id}: "
                        "Limited executable automation "
                        "could be inferred."
                    )
                )

            if not intent.assertions:
                warnings.append(
                    (
                        f"{test_case.test_case_id}: "
                        "No safe executable assertion "
                        "could be inferred."
                    )
                )

            playwright_tests.append(
                PlaywrightTest(
                    requirement_id=(
                        test_case.requirement_id
                    ),
                    test_case_id=(
                        test_case.test_case_id
                    ),
                    test_name=(
                        test_case.test_scenario
                    ),
                    scenario_type=(
                        test_case.scenario_type
                    ),
                    priority=(
                        test_case.priority
                    ),
                    actions=actions,
                    expected_result=(
                        test_case.expected_result
                    ),
                    source_criterion=(
                        test_case.source_criterion
                    ),
                )
            )

        code = self._render_typescript(
            tests=playwright_tests,
            intents=intents,
        )

        return PlaywrightGenerationResult(
            tests=playwright_tests,
            typescript_code=code,
            generated_test_count=len(
                playwright_tests
            ),
            warnings=warnings,
        )

    def _render_typescript(
        self,
        tests: list[PlaywrightTest],
        intents: dict[
            str,
            AutomationIntent,
        ],
    ) -> str:
        lines = [
            (
                "import { test, expect } "
                "from '@playwright/test';"
            ),
            "",
        ]

        for playwright_test in tests:
            safe_name = self._escape_string(
                (
                    f"{playwright_test.test_case_id} - "
                    f"{playwright_test.test_name}"
                )
            )

            lines.append(
                f"test('{safe_name}', "
                "async ({ page }) => {"
            )

            lines.append(
                "  // Requirement: "
                f"{playwright_test.requirement_id}"
            )

            lines.append(
                "  // Scenario: "
                f"{playwright_test.scenario_type}"
            )

            lines.append(
                "  // Priority: "
                f"{playwright_test.priority}"
            )

            for action in (
                playwright_test.actions
            ):
                rendered = (
                    self._render_action(
                        action
                    )
                )

                if rendered:
                    lines.append(
                        f"  {rendered}"
                    )

            intent = intents[
                playwright_test.test_case_id
            ]

            if intent.assertions:
                for assertion in (
                    intent.assertions
                ):
                    rendered = (
                        self._render_assertion(
                            assertion
                        )
                    )

                    if rendered:
                        lines.append(
                            f"  {rendered}"
                        )

            else:
                expected = (
                    self._escape_comment(
                        playwright_test.expected_result
                    )
                )

                lines.append(
                    "  // TODO: Configure "
                    "application-specific assertion "
                    f"for: {expected}"
                )

            lines.append("});")
            lines.append("")

        return "\n".join(lines)

    def _render_action(
        self,
        action: PlaywrightAction,
    ) -> str:
        if action.action_type == "goto":
            value = self._escape_string(
                action.value or "/"
            )

            return (
                f"await page.goto('{value}');"
            )

        if action.action_type == "click":
            locator = self._render_locator(
                action.locator
            )

            if locator:
                return (
                    f"await {locator}.click();"
                )

        if action.action_type == "fill":
            locator = self._render_locator(
                action.locator
            )

            if locator:
                value = self._escape_string(
                    action.value or ""
                )

                return (
                    f"await {locator}"
                    f".fill('{value}');"
                )

        if action.action_type == "select":
            locator = self._render_locator(
                action.locator
            )

            if locator:
                value = self._escape_string(
                    action.value or ""
                )

                return (
                    f"await {locator}"
                    f".selectOption('{value}');"
                )

        if action.action_type == "check":
            locator = self._render_locator(
                action.locator
            )

            if locator:
                return (
                    f"await {locator}.check();"
                )

        if action.action_type == "uncheck":
            locator = self._render_locator(
                action.locator
            )

            if locator:
                return (
                    f"await {locator}.uncheck();"
                )

        if action.action_type == "press":
            locator = self._render_locator(
                action.locator
            )

            if locator:
                value = self._escape_string(
                    action.value or ""
                )

                return (
                    f"await {locator}"
                    f".press('{value}');"
                )

        if (
            action.action_type
            == "set_input_files"
        ):
            locator = self._render_locator(
                action.locator
            )

            if locator:
                value = self._escape_string(
                    action.value or ""
                )

                return (
                    f"await {locator}"
                    f".setInputFiles('{value}');"
                )

        return ""

    def _render_assertion(
        self,
        assertion: AutomationAssertion,
    ) -> str:
        if (
            assertion.assertion_type
            == "url"
        ):
            value = self._escape_regex(
                assertion.expected_value
                or ""
            )

            return (
                "await expect(page)"
                f".toHaveURL(/{value}/);"
            )

        if (
            assertion.assertion_type
            == "visible_text"
        ):
            value = self._escape_string(
                assertion.expected_value
                or ""
            )

            return (
                "await expect("
                f"page.getByText('{value}')"
                ").toBeVisible();"
            )

        if (
            assertion.assertion_type
            == "field_value"
        ):
            label = self._field_label(
                assertion.target
            )

            if label is None:
                return ""

            value = self._escape_string(
                assertion.expected_value
                or ""
            )

            return (
                "await expect("
                f"page.getByLabel('{label}')"
                f").toHaveValue('{value}');"
            )

        if (
            assertion.assertion_type
            == "button_enabled"
        ):
            button_name = (
                self._escape_string(
                    assertion.target or ""
                )
            )

            return (
                "await expect("
                "page.getByRole("
                "'button', "
                f"{{ name: '{button_name}' }}"
                ")"
                ").toBeEnabled();"
            )

        return ""

    def _render_locator(
        self,
        locator: PlaywrightLocator | None,
    ) -> str:
        if locator is None:
            return ""

        value = self._escape_string(
            locator.value
        )

        if locator.locator_type == "label":
            return (
                f"page.getByLabel('{value}')"
            )

        if (
            locator.locator_type
            == "placeholder"
        ):
            return (
                "page.getByPlaceholder("
                f"'{value}')"
            )

        if locator.locator_type == "text":
            return (
                f"page.getByText('{value}')"
            )

        if (
            locator.locator_type
            == "test_id"
        ):
            return (
                f"page.getByTestId('{value}')"
            )

        if locator.locator_type == "css":
            return (
                f"page.locator('{value}')"
            )

        if locator.locator_type == "role":
            role_name = (
                self._escape_string(
                    locator.role_name or ""
                )
            )

            if role_name:
                return (
                    "page.getByRole("
                    f"'{value}', "
                    f"{{ name: '{role_name}' }}"
                    ")"
                )

            return (
                f"page.getByRole('{value}')"
            )

        return ""

    @staticmethod
    def _field_label(
        field: str | None,
    ) -> str | None:
        labels = {
            "username": "Username",
            "password": "Password",
            "email": "Email",
            "first_name": "First Name",
            "last_name": "Last Name",
            "phone": "Phone",
            "search": "Search",
        }

        if field is None:
            return None

        return labels.get(field)

    @staticmethod
    def _escape_string(
        value: str,
    ) -> str:
        return (
            value
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", " ")
        )

    @staticmethod
    def _escape_regex(
        value: str,
    ) -> str:
        return (
            value
            .replace("\\", "\\\\")
            .replace("/", "\\/")
            .replace(".", "\\.")
        )

    @staticmethod
    def _escape_comment(
        value: str,
    ) -> str:
        return (
            value
            .replace("\n", " ")
            .strip()
        )