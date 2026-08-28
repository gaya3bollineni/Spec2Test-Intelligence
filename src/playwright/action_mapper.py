from typing import Optional

from src.models.schemas import TestCase
from src.playwright.dom_models import DOMElement
from src.playwright.element_matcher import (
    DOMElementMatcher,
)
from src.playwright.intent import (
    AutomationIntent,
    AutomationIntentExtractor,
    AutomationInteraction,
)
from src.playwright.locator_generator import (
    DOMLocatorGenerator,
)
from src.playwright.models import (
    PlaywrightAction,
    PlaywrightLocator,
)


class PlaywrightActionMapper:
    """
    Converts structured automation intent into
    conservative Playwright actions.

    DOM elements may optionally be supplied.

    When DOM data is available, Spec2Test attempts
    to replace inferred locators with locators
    grounded in the supplied DOM.

    If no suitable DOM element is found, existing
    inferred locator behavior is preserved.
    """

    FIELD_LABELS = {
        "username": "Username",
        "password": "Password",
        "email": "Email",
        "first_name": "First Name",
        "last_name": "Last Name",
        "phone": "Phone",
        "search": "Search",
    }

    VALID_VALUES = {
        "username": "test_user",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone": "5551234567",
        "search": "test",
    }

    DEFAULT_ACTION_LABELS = {
        "login": "Login",
        "register": "Register",
        "submit": "Submit",
        "search": "Search",
        "save": "Save",
        "update": "Update",
        "delete": "Delete",
        "download": "Download",
    }

    def __init__(
        self,
    ) -> None:
        self.intent_extractor = (
            AutomationIntentExtractor()
        )

        self.element_matcher = (
            DOMElementMatcher()
        )

        self.locator_generator = (
            DOMLocatorGenerator()
        )

    def map_test_case(
        self,
        test_case: TestCase,
        dom_elements: Optional[
            list[DOMElement]
        ] = None,
    ) -> list[
        PlaywrightAction
    ]:
        intent = (
            self.intent_extractor.extract(
                test_case
            )
        )

        return self.map_intent(
            intent,
            dom_elements=dom_elements,
        )

    def map_intent(
        self,
        intent: AutomationIntent,
        dom_elements: Optional[
            list[DOMElement]
        ] = None,
    ) -> list[
        PlaywrightAction
    ]:
        actions: list[
            PlaywrightAction
        ] = []

        actions.append(
            PlaywrightAction(
                action_type="goto",
                value=intent.start_url,
                description=(
                    "Open application"
                ),
            )
        )

        explicit_fill_targets = {
            interaction.target.lower()
            for interaction
            in intent.interactions
            if (
                interaction.interaction_type
                == "fill"
            )
        }

        for field in intent.fields:
            label = (
                self.FIELD_LABELS.get(
                    field
                )
            )

            if (
                label
                and label.lower()
                in explicit_fill_targets
            ):
                continue

            field_action = (
                self._build_field_action(
                    field=field,
                    invalid_input=(
                        intent.invalid_input
                    ),
                    dom_elements=(
                        dom_elements
                    ),
                )
            )

            if field_action:
                actions.append(
                    field_action
                )

        for interaction in (
            intent.interactions
        ):
            interaction_action = (
                self._build_interaction_action(
                    interaction=interaction,
                    invalid_input=(
                        intent.invalid_input
                    ),
                    dom_elements=(
                        dom_elements
                    ),
                )
            )

            if interaction_action:
                actions.append(
                    interaction_action
                )

        if intent.primary_action:
            primary_action = (
                self._build_primary_action(
                    action=(
                        intent.primary_action
                    ),
                    action_label=(
                        intent.action_label
                    ),
                    dom_elements=(
                        dom_elements
                    ),
                )
            )

            if primary_action:
                actions.append(
                    primary_action
                )

        return (
            self._deduplicate_actions(
                actions
            )
        )

    def _build_field_action(
        self,
        field: str,
        invalid_input: bool,
        dom_elements: Optional[
            list[DOMElement]
        ] = None,
    ) -> PlaywrightAction | None:
        label = (
            self.FIELD_LABELS.get(
                field
            )
        )

        if label is None:
            return None

        if invalid_input:
            value = (
                self._invalid_value(
                    field
                )
            )
        else:
            value = (
                self.VALID_VALUES.get(
                    field,
                    "test_value",
                )
            )

        inferred_locator = (
            PlaywrightLocator(
                locator_type="label",
                value=label,
            )
        )

        locator = (
            self._resolve_locator(
                target=label,
                fallback=(
                    inferred_locator
                ),
                dom_elements=(
                    dom_elements
                ),
                expected_tag="input",
            )
        )

        return PlaywrightAction(
            action_type="fill",
            locator=locator,
            value=value,
            description=(
                f"Enter value into "
                f"{label}"
            ),
        )

    def _build_interaction_action(
        self,
        interaction: (
            AutomationInteraction
        ),
        invalid_input: bool,
        dom_elements: Optional[
            list[DOMElement]
        ] = None,
    ) -> PlaywrightAction | None:
        interaction_type = (
            interaction.interaction_type
        )

        if interaction_type == "fill":
            value = (
                "invalid_value"
                if invalid_input
                else interaction.value
            )

            fallback = (
                PlaywrightLocator(
                    locator_type="label",
                    value=(
                        interaction.target
                    ),
                )
            )

            locator = (
                self._resolve_locator(
                    target=(
                        interaction.target
                    ),
                    fallback=fallback,
                    dom_elements=(
                        dom_elements
                    ),
                    expected_tag="input",
                )
            )

            return PlaywrightAction(
                action_type="fill",
                locator=locator,
                value=value,
                description=(
                    f"Enter value into "
                    f"{interaction.target}"
                ),
            )

        if interaction_type == "select":
            fallback = (
                PlaywrightLocator(
                    locator_type="label",
                    value=(
                        interaction.target
                    ),
                )
            )

            locator = (
                self._resolve_locator(
                    target=(
                        interaction.target
                    ),
                    fallback=fallback,
                    dom_elements=(
                        dom_elements
                    ),
                    expected_tag="select",
                )
            )

            return PlaywrightAction(
                action_type="select",
                locator=locator,
                value=interaction.value,
                description=(
                    f"Select "
                    f"{interaction.value} "
                    f"from "
                    f"{interaction.target}"
                ),
            )

        if interaction_type == "check":
            fallback = (
                PlaywrightLocator(
                    locator_type="label",
                    value=(
                        interaction.target
                    ),
                )
            )

            locator = (
                self._resolve_locator(
                    target=(
                        interaction.target
                    ),
                    fallback=fallback,
                    dom_elements=(
                        dom_elements
                    ),
                    expected_tag="input",
                    expected_type=(
                        "checkbox"
                    ),
                )
            )

            return PlaywrightAction(
                action_type="check",
                locator=locator,
                description=(
                    f"Check "
                    f"{interaction.target}"
                ),
            )

        if interaction_type == "uncheck":
            fallback = (
                PlaywrightLocator(
                    locator_type="label",
                    value=(
                        interaction.target
                    ),
                )
            )

            locator = (
                self._resolve_locator(
                    target=(
                        interaction.target
                    ),
                    fallback=fallback,
                    dom_elements=(
                        dom_elements
                    ),
                    expected_tag="input",
                    expected_type=(
                        "checkbox"
                    ),
                )
            )

            return PlaywrightAction(
                action_type="uncheck",
                locator=locator,
                description=(
                    f"Uncheck "
                    f"{interaction.target}"
                ),
            )

        if interaction_type == "radio":
            fallback = (
                PlaywrightLocator(
                    locator_type="label",
                    value=(
                        interaction.target
                    ),
                )
            )

            locator = (
                self._resolve_locator(
                    target=(
                        interaction.target
                    ),
                    fallback=fallback,
                    dom_elements=(
                        dom_elements
                    ),
                    expected_tag="input",
                    expected_type="radio",
                )
            )

            return PlaywrightAction(
                action_type="check",
                locator=locator,
                description=(
                    f"Select radio option "
                    f"{interaction.target}"
                ),
            )

        if interaction_type == "link":
            fallback = (
                PlaywrightLocator(
                    locator_type="role",
                    value="link",
                    role_name=(
                        interaction.target
                    ),
                )
            )

            locator = (
                self._resolve_locator(
                    target=(
                        interaction.target
                    ),
                    fallback=fallback,
                    dom_elements=(
                        dom_elements
                    ),
                    expected_tag="a",
                )
            )

            return PlaywrightAction(
                action_type="click",
                locator=locator,
                description=(
                    f"Click link "
                    f"{interaction.target}"
                ),
            )

        if interaction_type == "press":
            fallback = (
                PlaywrightLocator(
                    locator_type="label",
                    value=(
                        interaction.target
                    ),
                )
            )

            locator = (
                self._resolve_locator(
                    target=(
                        interaction.target
                    ),
                    fallback=fallback,
                    dom_elements=(
                        dom_elements
                    ),
                    expected_tag="input",
                )
            )

            return PlaywrightAction(
                action_type="press",
                locator=locator,
                value=interaction.value,
                description=(
                    f"Press "
                    f"{interaction.value} "
                    f"in "
                    f"{interaction.target}"
                ),
            )

        if interaction_type == "upload":
            fallback = (
                PlaywrightLocator(
                    locator_type="label",
                    value=(
                        interaction.target
                    ),
                )
            )

            locator = (
                self._resolve_locator(
                    target=(
                        interaction.target
                    ),
                    fallback=fallback,
                    dom_elements=(
                        dom_elements
                    ),
                    expected_tag="input",
                    expected_type="file",
                )
            )

            return PlaywrightAction(
                action_type=(
                    "set_input_files"
                ),
                locator=locator,
                value=interaction.value,
                description=(
                    f"Upload "
                    f"{interaction.value} "
                    f"to "
                    f"{interaction.target}"
                ),
            )

        return None

    def _build_primary_action(
        self,
        action: str,
        action_label: (
            str | None
        ),
        dom_elements: Optional[
            list[DOMElement]
        ] = None,
    ) -> PlaywrightAction | None:
        label = (
            action_label
            or self.DEFAULT_ACTION_LABELS.get(
                action
            )
        )

        if label is None:
            return None

        fallback = (
            PlaywrightLocator(
                locator_type="role",
                value="button",
                role_name=label,
            )
        )

        locator = (
            self._resolve_locator(
                target=label,
                fallback=fallback,
                dom_elements=(
                    dom_elements
                ),
                expected_tag="button",
            )
        )

        return PlaywrightAction(
            action_type="click",
            locator=locator,
            description=(
                f"Click {label}"
            ),
        )

    def _resolve_locator(
        self,
        target: str,
        fallback: PlaywrightLocator,
        dom_elements: Optional[
            list[DOMElement]
        ],
        expected_tag: str | None = None,
        expected_type: str | None = None,
    ) -> PlaywrightLocator:
        """
        Attempts to ground the locator in supplied
        DOM data.

        Existing inferred behavior is preserved when
        DOM data is absent or no usable match exists.
        """

        if not dom_elements:
            return fallback

        match = (
            self.element_matcher.match(
                target=target,
                elements=dom_elements,
                expected_tag=(
                    expected_tag
                ),
                expected_type=(
                    expected_type
                ),
            )
        )

        if match is None:
            return fallback

        locator = (
            self.locator_generator.generate(
                match.element
            )
        )

        if locator is None:
            return fallback

        return locator

    def _invalid_value(
        self,
        field: str,
    ) -> str:
        invalid_values = {
            "username": "invalid_user",
            "password": (
                "invalid_password"
            ),
            "email": "invalid-email",
            "first_name": "",
            "last_name": "",
            "phone": "invalid_phone",
            "search": "invalid_search",
        }

        return (
            invalid_values.get(
                field,
                "invalid_value",
            )
        )

    def _deduplicate_actions(
        self,
        actions: list[
            PlaywrightAction
        ],
    ) -> list[
        PlaywrightAction
    ]:
        unique_actions: list[
            PlaywrightAction
        ] = []

        seen: set[str] = set()

        for action in actions:
            signature = (
                action.model_dump_json(
                    exclude={
                        "description",
                    }
                )
            )

            if signature in seen:
                continue

            seen.add(
                signature
            )

            unique_actions.append(
                action
            )

        return unique_actions