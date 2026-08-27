import re
from typing import Literal

from pydantic import BaseModel, Field

from src.models.schemas import TestCase


AssertionType = Literal[
    "url",
    "visible_text",
    "field_value",
    "button_enabled",
]


class AutomationAssertion(BaseModel):
    assertion_type: AssertionType
    target: str | None = None
    expected_value: str | None = None


class AutomationIntent(BaseModel):
    fields: list[str] = Field(
        default_factory=list
    )

    primary_action: str | None = None
    action_label: str | None = None

    start_url: str = "/"

    assertions: list[AutomationAssertion] = Field(
        default_factory=list
    )

    invalid_input: bool = False


class AutomationIntentExtractor:
    """
    Extracts conservative browser-automation intent from
    a Spec2Test test case.

    Spec2Test does not inspect the application's DOM.
    """

    FIELD_PATTERNS = {
        "username": (
            "username",
            "user name",
        ),
        "password": (
            "password",
        ),
        "email": (
            "email",
            "email address",
        ),
        "first_name": (
            "first name",
        ),
        "last_name": (
            "last name",
        ),
        "phone": (
            "phone",
            "phone number",
        ),
        "search": (
            "search field",
            "search box",
            "search term",
        ),
    }

    ACTION_PATTERNS = {
        "login": (
            "log in",
            "login",
            "sign in",
        ),
        "register": (
            "register",
            "sign up",
        ),
        "submit": (
            "submit",
        ),
        "search": (
            "search",
        ),
        "save": (
            "save",
        ),
        "update": (
            "update",
        ),
        "delete": (
            "delete",
        ),
        "upload": (
            "upload",
        ),
        "download": (
            "download",
        ),
    }

    ACTION_LABELS = {
        "log in": "Log in",
        "login": "Login",
        "sign in": "Sign in",
        "register": "Register",
        "sign up": "Sign up",
        "submit": "Submit",
        "search": "Search",
        "save": "Save",
        "update": "Update",
        "delete": "Delete",
        "upload": "Upload",
        "download": "Download",
    }

    def extract(
        self,
        test_case: TestCase,
    ) -> AutomationIntent:
        combined_text = self._build_context(
            test_case
        )

        action_context = self._build_action_context(
            test_case
        )

        fields = self._extract_fields(
            combined_text
        )

        primary_action = self._extract_action(
            action_context
        )

        action_label = self._extract_action_label(
            action_context
        )

        start_url = self._extract_start_url(
            test_case.source_criterion
        )

        invalid_input = self._is_invalid_scenario(
            test_case
        )

        assertions = self._extract_assertions(
            test_case
        )

        return AutomationIntent(
            fields=fields,
            primary_action=primary_action,
            action_label=action_label,
            start_url=start_url,
            assertions=assertions,
            invalid_input=invalid_input,
        )

    def _build_context(
        self,
        test_case: TestCase,
    ) -> str:
        parts = [
            test_case.source_criterion,
            test_case.test_scenario,
            test_case.test_case_description,
            " ".join(test_case.test_steps),
            test_case.test_data,
            test_case.expected_result,
        ]

        return " ".join(
            part
            for part in parts
            if part
        ).lower()

    def _build_action_context(
        self,
        test_case: TestCase,
    ) -> str:
        return " ".join(
            [
                test_case.source_criterion,
                test_case.test_scenario,
                " ".join(test_case.test_steps),
            ]
        ).lower()

    def _extract_fields(
        self,
        text: str,
    ) -> list[str]:
        fields: list[str] = []

        for field, patterns in (
            self.FIELD_PATTERNS.items()
        ):
            if any(
                pattern in text
                for pattern in patterns
            ):
                fields.append(field)

        return fields

    def _extract_action(
        self,
        text: str,
    ) -> str | None:
        for action, patterns in (
            self.ACTION_PATTERNS.items()
        ):
            if any(
                pattern in text
                for pattern in patterns
            ):
                return action

        return None

    def _extract_action_label(
        self,
        text: str,
    ) -> str | None:
        # Longer phrases first so "sign in" wins
        # over any shorter overlapping phrase.
        phrases = sorted(
            self.ACTION_LABELS.keys(),
            key=len,
            reverse=True,
        )

        for phrase in phrases:
            if phrase in text:
                return self.ACTION_LABELS[
                    phrase
                ]

        return None

    def _extract_start_url(
        self,
        source_criterion: str,
    ) -> str:
        text = source_criterion.strip()

        full_url_match = re.search(
            r"https?://[^\s,]+",
            text,
            re.IGNORECASE,
        )

        if full_url_match:
            return (
                full_url_match
                .group(0)
                .rstrip(".")
            )

        domain_match = re.search(
            r"\b(?:www\.)?"
            r"[a-z0-9][a-z0-9.-]*"
            r"\.[a-z]{2,}"
            r"(?:/[^\s,]*)?",
            text,
            re.IGNORECASE,
        )

        if domain_match:
            domain = (
                domain_match
                .group(0)
                .rstrip(".")
            )

            return f"https://{domain}"

        return "/"

    def _extract_assertions(
        self,
        test_case: TestCase,
    ) -> list[AutomationAssertion]:
        # Assertions must come from the scenario-specific
        # expected result. We do not invent assertions from
        # generic generated behavior.
        expected = (
            test_case.expected_result
            .strip()
        )

        if not expected:
            return []

        url_assertion = (
            self._extract_url_assertion(
                expected
            )
        )

        if url_assertion is not None:
            return [
                url_assertion
            ]

        field_assertion = (
            self._extract_field_value_assertion(
                expected
            )
        )

        if field_assertion is not None:
            return [
                field_assertion
            ]

        button_assertion = (
            self._extract_button_assertion(
                expected
            )
        )

        if button_assertion is not None:
            return [
                button_assertion
            ]

        text_assertion = (
            self._extract_visible_text_assertion(
                expected
            )
        )

        if text_assertion is not None:
            return [
                text_assertion
            ]

        return []

    def _extract_url_assertion(
        self,
        text: str,
    ) -> AutomationAssertion | None:
        normalized = text.lower()

        # Includes a few common misspellings found in
        # manually written acceptance criteria.
        redirect_words = (
            "redirected",
            "redirect",
            "navigated",
            "navigate",
            "recirected",
            "rediected",
        )

        if not any(
            word in normalized
            for word in redirect_words
        ):
            return None

        match = re.search(
            r"(?:redirected|redirect|navigated|navigate|"
            r"recirected|rediected)"
            r".*?\bto\s+(?:the\s+)?"
            r"([a-z0-9 _-]+?)\s+page\b",
            normalized,
        )

        if not match:
            return None

        page_name = (
            match.group(1)
            .strip()
            .replace(" ", "-")
        )

        return AutomationAssertion(
            assertion_type="url",
            expected_value=f"/{page_name}",
        )

    def _extract_visible_text_assertion(
        self,
        text: str,
    ) -> AutomationAssertion | None:
        # Only create text assertions when the requirement
        # gives explicit quoted text.
        quoted_match = re.search(
            r"""["']([^"']+)["']""",
            text,
        )

        if not quoted_match:
            return None

        lower = text.lower()

        if not any(
            word in lower
            for word in (
                "display",
                "displayed",
                "shown",
                "visible",
                "see",
            )
        ):
            return None

        return AutomationAssertion(
            assertion_type="visible_text",
            expected_value=(
                quoted_match.group(1)
            ),
        )

    def _extract_field_value_assertion(
        self,
        text: str,
    ) -> AutomationAssertion | None:
        lower = text.lower()

        for field, patterns in (
            self.FIELD_PATTERNS.items()
        ):
            if not any(
                pattern in lower
                for pattern in patterns
            ):
                continue

            if (
                "empty" in lower
                or "blank" in lower
            ):
                return AutomationAssertion(
                    assertion_type="field_value",
                    target=field,
                    expected_value="",
                )

        return None

    def _extract_button_assertion(
        self,
        text: str,
    ) -> AutomationAssertion | None:
        lower = text.lower()

        if "button" not in lower:
            return None

        if "enabled" not in lower:
            return None

        match = re.search(
            r"([a-z0-9 _-]+?)\s+button",
            text,
            re.IGNORECASE,
        )

        if not match:
            return None

        button_name = (
            match.group(1)
            .strip()
            .title()
        )

        return AutomationAssertion(
            assertion_type="button_enabled",
            target=button_name,
        )

    def _is_invalid_scenario(
        self,
        test_case: TestCase,
    ) -> bool:
        scenario_type = (
            test_case.scenario_type
            .strip()
            .lower()
        )

        if scenario_type == "negative":
            return True

        scenario_context = " ".join(
            [
                test_case.test_scenario,
                test_case.test_case_description,
                " ".join(
                    test_case.test_steps
                ),
                test_case.test_data,
            ]
        ).lower()

        return (
            "invalid" in scenario_context
            or "incorrect" in scenario_context
        )