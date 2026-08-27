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

InteractionType = Literal[
    "fill",
    "select",
    "check",
    "uncheck",
    "radio",
    "link",
    "press",
    "upload",
]


class AutomationAssertion(
    BaseModel
):
    assertion_type: AssertionType
    target: str | None = None
    expected_value: str | None = None


class AutomationInteraction(
    BaseModel
):
    interaction_type: InteractionType
    target: str
    value: str | None = None


class AutomationIntent(
    BaseModel
):
    fields: list[str] = Field(
        default_factory=list
    )

    primary_action: str | None = None
    action_label: str | None = None

    start_url: str = "/"

    interactions: list[
        AutomationInteraction
    ] = Field(
        default_factory=list
    )

    assertions: list[
        AutomationAssertion
    ] = Field(
        default_factory=list
    )

    invalid_input: bool = False


class AutomationIntentExtractor:
    """
    Extracts conservative browser automation intent
    from one Spec2Test test case.

    Extraction is scoped to the current requirement.
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

    ACTION_REGEX_PATTERNS = {
        "login": (
            r"\b(?:log in|login|sign in)\b"
        ),
        "register": (
            r"\b(?:register|sign up)\b"
        ),
        "submit": (
            r"\b(?:submit|submits)\b"
        ),
        "search": (
            r"\b(?:search(?:es)? for|"
            r"clicks?\s+(?:on\s+)?search"
            r"(?:\s+button)?)\b"
        ),
        "save": (
            r"\b(?:save|saves)\b"
        ),
        "update": (
            r"\b(?:update|updates)\b"
        ),
        "delete": (
            r"\b(?:delete|deletes)\b"
        ),
        "download": (
            r"\b(?:download|downloads)\b"
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
        "download": "Download",
    }

    def extract(
        self,
        test_case: TestCase,
    ) -> AutomationIntent:
        combined_text = (
            self._build_context(
                test_case
            )
        )

        action_context = (
            self._build_action_context(
                test_case
            )
        )

        fields = self._extract_fields(
            combined_text
        )

        primary_action = (
            self._extract_action(
                action_context
            )
        )

        action_label = None

        if primary_action:
            action_label = (
                self._extract_action_label(
                    action_context
                )
            )

        start_url = (
            self._extract_start_url(
                test_case.source_criterion
            )
        )

        interactions = (
            self._extract_interactions(
                test_case.source_criterion
            )
        )

        invalid_input = (
            self._is_invalid_scenario(
                test_case
            )
        )

        assertions = (
            self._extract_assertions(
                test_case
            )
        )

        return AutomationIntent(
            fields=fields,
            primary_action=primary_action,
            action_label=action_label,
            start_url=start_url,
            interactions=interactions,
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
            " ".join(
                test_case.test_steps
            ),
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
        text = " ".join(
            [
                test_case.source_criterion,
                test_case.test_scenario,
                " ".join(
                    test_case.test_steps
                ),
            ]
        )

        # URL paths such as /register or /search
        # are navigation context, not user actions.
        text = self._remove_urls(
            text
        )

        return text.lower()

    @staticmethod
    def _remove_urls(
        text: str,
    ) -> str:
        text = re.sub(
            r"https?://\S+",
            " ",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\b(?:www\.)?"
            r"[a-z0-9][a-z0-9.-]*"
            r"\.[a-z]{2,}"
            r"(?:/[^\s,]*)?",
            " ",
            text,
            flags=re.IGNORECASE,
        )

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

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
                fields.append(
                    field
                )

        return fields

    def _extract_action(
        self,
        text: str,
    ) -> str | None:
        for action, pattern in (
            self.ACTION_REGEX_PATTERNS.items()
        ):
            if re.search(
                pattern,
                text,
                re.IGNORECASE,
            ):
                return action

        return None

    def _extract_action_label(
        self,
        text: str,
    ) -> str | None:
        phrases = sorted(
            self.ACTION_LABELS.keys(),
            key=len,
            reverse=True,
        )

        for phrase in phrases:
            if re.search(
                rf"\b{re.escape(phrase)}\b",
                text,
                re.IGNORECASE,
            ):
                return (
                    self.ACTION_LABELS[
                        phrase
                    ]
                )

        return None

    def _extract_start_url(
        self,
        source_criterion: str,
    ) -> str:
        text = (
            source_criterion.strip()
        )

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

            return (
                f"https://{domain}"
            )

        return "/"

    def _extract_interactions(
        self,
        text: str,
    ) -> list[
        AutomationInteraction
    ]:
        """
        Extracts every explicit interaction from the
        current requirement and preserves source order.
        """

        candidates: list[
            tuple[
                int,
                AutomationInteraction,
            ]
        ] = []

        candidates.extend(
            self._find_fill_interactions(
                text
            )
        )

        candidates.extend(
            self._find_upload_interactions(
                text
            )
        )

        candidates.extend(
            self._find_press_interactions(
                text
            )
        )

        candidates.extend(
            self._find_select_interactions(
                text
            )
        )

        candidates.extend(
            self._find_uncheck_interactions(
                text
            )
        )

        candidates.extend(
            self._find_checkbox_interactions(
                text
            )
        )

        candidates.extend(
            self._find_radio_interactions(
                text
            )
        )

        candidates.extend(
            self._find_link_interactions(
                text
            )
        )

        candidates.sort(
            key=lambda item: item[0]
        )

        interactions: list[
            AutomationInteraction
        ] = []

        seen: set[str] = set()

        for _, interaction in candidates:
            signature = (
                interaction.model_dump_json()
            )

            if signature in seen:
                continue

            seen.add(
                signature
            )

            interactions.append(
                interaction
            )

        return interactions

    def _find_fill_interactions(
        self,
        text: str,
    ) -> list[
        tuple[
            int,
            AutomationInteraction,
        ]
    ]:
        results = []

        pattern = re.compile(
            r"\b(?:user\s+)?"
            r"(?:enters?|types?|fills?)\s+"
            r"""["']?(.+?)["']?\s+"""
            r"(?:into|in)\s+"
            r"(?:the\s+)?"
            r"(.+?)"
            r"(?=\s+(?:"
            r"and\s+(?:user\s+)?"
            r"(?:enters?|types?|fills?|"
            r"selects?|chooses?|checks?|"
            r"unchecks?|clicks?|press(?:es)?|"
            r"uploads?)"
            r"|then\b|when\b|given\b"
            r")|[.,]|$)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(
            text
        ):
            value = (
                match.group(1)
                .strip()
                .strip("\"'")
            )

            target = self._clean_label(
                match.group(2)
            )

            if not value or not target:
                continue

            results.append(
                (
                    match.start(),
                    AutomationInteraction(
                        interaction_type=(
                            "fill"
                        ),
                        target=target,
                        value=value,
                    ),
                )
            )

        return results

    def _find_upload_interactions(
        self,
        text: str,
    ) -> list[
        tuple[
            int,
            AutomationInteraction,
        ]
    ]:
        results = []

        pattern = re.compile(
            r"\buploads?\s+"
            r"""["']?([^"'\s]+)["']?\s+"""
            r"(?:to|into)\s+"
            r"(?:the\s+)?"
            r"(.+?)"
            r"(?=\s+(?:and\s+|then\b|"
            r"when\b|given\b)|[.,]|$)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(
            text
        ):
            file_name = (
                match.group(1)
                .strip()
            )

            target = self._clean_label(
                match.group(2)
            )

            results.append(
                (
                    match.start(),
                    AutomationInteraction(
                        interaction_type=(
                            "upload"
                        ),
                        target=target,
                        value=file_name,
                    ),
                )
            )

        return results

    def _find_press_interactions(
        self,
        text: str,
    ) -> list[
        tuple[
            int,
            AutomationInteraction,
        ]
    ]:
        results = []

        pattern = re.compile(
            r"\bpress(?:es)?\s+"
            r"(Enter|Tab|Escape|ArrowDown|"
            r"ArrowUp|ArrowLeft|ArrowRight|"
            r"Space)\s+"
            r"(?:in|on)\s+"
            r"(?:the\s+)?"
            r"(.+?)"
            r"(?=\s+(?:and\s+|then\b|"
            r"when\b|given\b)|[.,]|$)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(
            text
        ):
            results.append(
                (
                    match.start(),
                    AutomationInteraction(
                        interaction_type=(
                            "press"
                        ),
                        target=(
                            self._clean_label(
                                match.group(2)
                            )
                        ),
                        value=(
                            self._normalize_key(
                                match.group(1)
                            )
                        ),
                    ),
                )
            )

        return results

    def _find_select_interactions(
        self,
        text: str,
    ) -> list[
        tuple[
            int,
            AutomationInteraction,
        ]
    ]:
        results = []

        pattern = re.compile(
            r"\bselects?\s+"
            r"(.+?)\s+from\s+"
            r"(?:the\s+)?"
            r"(.+?)"
            r"(?=\s+(?:and\s+|then\b|"
            r"when\b|given\b)|[.,]|$)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(
            text
        ):
            results.append(
                (
                    match.start(),
                    AutomationInteraction(
                        interaction_type=(
                            "select"
                        ),
                        target=(
                            self._clean_label(
                                match.group(2)
                            )
                        ),
                        value=(
                            match.group(1)
                            .strip()
                        ),
                    ),
                )
            )

        return results

    def _find_uncheck_interactions(
        self,
        text: str,
    ) -> list[
        tuple[
            int,
            AutomationInteraction,
        ]
    ]:
        results = []

        pattern = re.compile(
            r"\bunchecks?\s+"
            r"(?:the\s+)?"
            r"(.+?)"
            r"(?=\s+(?:and\s+|then\b|"
            r"when\b|given\b)|[.,]|$)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(
            text
        ):
            results.append(
                (
                    match.start(),
                    AutomationInteraction(
                        interaction_type=(
                            "uncheck"
                        ),
                        target=(
                            self._clean_label(
                                match.group(1)
                            )
                        ),
                    ),
                )
            )

        return results

    def _find_checkbox_interactions(
        self,
        text: str,
    ) -> list[
        tuple[
            int,
            AutomationInteraction,
        ]
    ]:
        results = []

        pattern = re.compile(
            r"\bchecks?\s+"
            r"(?:the\s+)?"
            r"(.+?)"
            r"(?=\s+(?:and\s+|then\b|"
            r"when\b|given\b)|[.,]|$)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(
            text
        ):
            results.append(
                (
                    match.start(),
                    AutomationInteraction(
                        interaction_type=(
                            "check"
                        ),
                        target=(
                            self._clean_label(
                                match.group(1)
                            )
                        ),
                    ),
                )
            )

        return results

    def _find_radio_interactions(
        self,
        text: str,
    ) -> list[
        tuple[
            int,
            AutomationInteraction,
        ]
    ]:
        results = []

        pattern = re.compile(
            r"\b(?:selects?|chooses?)\s+"
            r"(?:the\s+)?"
            r"(.+?)\s+"
            r"radio(?:\s+button)?"
            r"(?=\s+(?:and\s+|then\b|"
            r"when\b|given\b)|[.,]|$)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(
            text
        ):
            results.append(
                (
                    match.start(),
                    AutomationInteraction(
                        interaction_type=(
                            "radio"
                        ),
                        target=(
                            self._clean_label(
                                match.group(1)
                            )
                        ),
                    ),
                )
            )

        return results

    def _find_link_interactions(
        self,
        text: str,
    ) -> list[
        tuple[
            int,
            AutomationInteraction,
        ]
    ]:
        results = []

        pattern = re.compile(
            r"\bclicks?\s+(?:on\s+)?"
            r"(?:the\s+)?"
            r"(.+?)\s+link"
            r"(?=\s+(?:and\s+|then\b|"
            r"when\b|given\b)|[.,]|$)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(
            text
        ):
            results.append(
                (
                    match.start(),
                    AutomationInteraction(
                        interaction_type=(
                            "link"
                        ),
                        target=(
                            self._clean_label(
                                match.group(1)
                            )
                        ),
                    ),
                )
            )

        return results

    @staticmethod
    def _normalize_key(
        value: str,
    ) -> str:
        mapping = {
            "enter": "Enter",
            "tab": "Tab",
            "escape": "Escape",
            "arrowdown": "ArrowDown",
            "arrowup": "ArrowUp",
            "arrowleft": "ArrowLeft",
            "arrowright": "ArrowRight",
            "space": "Space",
        }

        return mapping.get(
            value.lower(),
            value,
        )

    @staticmethod
    def _clean_label(
        value: str,
    ) -> str:
        cleaned = re.sub(
            r"\s+",
            " ",
            value,
        ).strip(" .")

        cleaned = re.sub(
            r"\s+(?:field|textbox|input|"
            r"dropdown|list|checkbox)$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        return cleaned.title()

    def _extract_assertions(
        self,
        test_case: TestCase,
    ) -> list[
        AutomationAssertion
    ]:
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

        if url_assertion:
            return [
                url_assertion
            ]

        field_assertion = (
            self._extract_field_value_assertion(
                expected
            )
        )

        if field_assertion:
            return [
                field_assertion
            ]

        button_assertion = (
            self._extract_button_assertion(
                expected
            )
        )

        if button_assertion:
            return [
                button_assertion
            ]

        text_assertion = (
            self._extract_visible_text_assertion(
                expected
            )
        )

        if text_assertion:
            return [
                text_assertion
            ]

        return []

    def _extract_url_assertion(
        self,
        text: str,
    ) -> AutomationAssertion | None:
        normalized = text.lower()

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
            r"(?:redirected|redirect|"
            r"navigated|navigate|"
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
            .replace(
                " ",
                "-",
            )
        )

        return AutomationAssertion(
            assertion_type="url",
            expected_value=(
                f"/{page_name}"
            ),
        )

    def _extract_visible_text_assertion(
        self,
        text: str,
    ) -> AutomationAssertion | None:
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
            assertion_type=(
                "visible_text"
            ),
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
                    assertion_type=(
                        "field_value"
                    ),
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

        return AutomationAssertion(
            assertion_type=(
                "button_enabled"
            ),
            target=(
                match.group(1)
                .strip()
                .title()
            ),
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
            "invalid"
            in scenario_context
            or "incorrect"
            in scenario_context
        )