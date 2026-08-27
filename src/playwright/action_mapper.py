from src.models.schemas import TestCase
from src.playwright.intent import (
    AutomationIntent,
    AutomationIntentExtractor,
)
from src.playwright.models import (
    PlaywrightAction,
    PlaywrightLocator,
)


class PlaywrightActionMapper:
    """
    Converts structured automation intent into
    conservative Playwright actions.
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
        "upload": "Upload",
        "download": "Download",
    }

    def __init__(self) -> None:
        self.intent_extractor = (
            AutomationIntentExtractor()
        )

    def map_test_case(
        self,
        test_case: TestCase,
    ) -> list[PlaywrightAction]:
        intent = self.intent_extractor.extract(
            test_case
        )

        return self.map_intent(
            intent
        )

    def map_intent(
        self,
        intent: AutomationIntent,
    ) -> list[PlaywrightAction]:
        actions: list[PlaywrightAction] = []

        actions.append(
            PlaywrightAction(
                action_type="goto",
                value=intent.start_url,
                description="Open application",
            )
        )

        for field in intent.fields:
            field_action = (
                self._build_field_action(
                    field=field,
                    invalid_input=(
                        intent.invalid_input
                    ),
                )
            )

            if field_action is not None:
                actions.append(
                    field_action
                )

        if intent.primary_action:
            primary_action = (
                self._build_primary_action(
                    action=intent.primary_action,
                    action_label=(
                        intent.action_label
                    ),
                )
            )

            if primary_action is not None:
                actions.append(
                    primary_action
                )

        return self._deduplicate_actions(
            actions
        )

    def _build_field_action(
        self,
        field: str,
        invalid_input: bool,
    ) -> PlaywrightAction | None:
        label = self.FIELD_LABELS.get(
            field
        )

        if label is None:
            return None

        if invalid_input:
            value = self._invalid_value(
                field
            )
        else:
            value = self.VALID_VALUES.get(
                field,
                "test_value",
            )

        return PlaywrightAction(
            action_type="fill",
            locator=PlaywrightLocator(
                locator_type="label",
                value=label,
            ),
            value=value,
            description=(
                f"Enter value into {label}"
            ),
        )

    def _build_primary_action(
        self,
        action: str,
        action_label: str | None,
    ) -> PlaywrightAction | None:
        label = (
            action_label
            or self.DEFAULT_ACTION_LABELS.get(
                action
            )
        )

        if label is None:
            return None

        return PlaywrightAction(
            action_type="click",
            locator=PlaywrightLocator(
                locator_type="role",
                value="button",
                role_name=label,
            ),
            description=f"Click {label}",
        )

    def _invalid_value(
        self,
        field: str,
    ) -> str:
        invalid_values = {
            "username": "invalid_user",
            "password": "invalid_password",
            "email": "invalid-email",
            "first_name": "",
            "last_name": "",
            "phone": "invalid_phone",
            "search": "invalid_search",
        }

        return invalid_values.get(
            field,
            "invalid_value",
        )

    def _deduplicate_actions(
        self,
        actions: list[PlaywrightAction],
    ) -> list[PlaywrightAction]:
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