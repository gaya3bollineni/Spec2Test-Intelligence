from src.models.schemas import TestCase as Spec2TestCase
from src.playwright.action_mapper import PlaywrightActionMapper
from src.playwright.intent import AutomationIntent


def build_test_case(
    scenario_type: str = "Positive",
) -> Spec2TestCase:
    return Spec2TestCase(
        test_case_id="TC-001-P1",
        requirement_id="AC-001",
        scenario_type=scenario_type,
        test_scenario="Validate user sign in",
        test_case_description=(
            "Validate sign in with username and password."
        ),
        preconditions=[],
        test_steps=[
            "User clicks on sign in.",
            "User enters username and password.",
        ],
        test_data="Valid credentials",
        expected_result=(
            "Verify user is redirected to home page."
        ),
        priority="Medium",
        source_criterion=(
            "Given user is mail.google.com "
            "When user clicks on sign in "
            "And enters username and password "
            "Then verify user is redirected to home page"
        ),
    )


def test_maps_login_test_case() -> None:
    mapper = PlaywrightActionMapper()

    actions = mapper.map_test_case(
        build_test_case()
    )

    assert len(actions) == 4

    assert actions[0].action_type == "goto"
    assert (
        actions[0].value
        == "https://mail.google.com"
    )

    assert actions[1].action_type == "fill"
    assert actions[1].locator is not None
    assert actions[1].locator.value == "Username"
    assert actions[1].value == "test_user"

    assert actions[2].action_type == "fill"
    assert actions[2].locator is not None
    assert actions[2].locator.value == "Password"
    assert (
        actions[2].value
        == "TestPassword123!"
    )

    assert actions[3].action_type == "click"
    assert actions[3].locator is not None
    assert actions[3].locator.value == "button"
    assert (
        actions[3].locator.role_name
        == "Sign in"
    )


def test_negative_login_uses_invalid_values() -> None:
    mapper = PlaywrightActionMapper()

    test_case = build_test_case(
        scenario_type="Negative"
    )

    test_case.test_case_id = "TC-001-N1"

    actions = mapper.map_test_case(
        test_case
    )

    assert (
        actions[1].value
        == "invalid_user"
    )

    assert (
        actions[2].value
        == "invalid_password"
    )


def test_intent_generates_single_navigation() -> None:
    mapper = PlaywrightActionMapper()

    intent = AutomationIntent(
        fields=[
            "username",
            "password",
        ],
        primary_action="login",
        action_label="Sign in",
        start_url="https://example.com",
    )

    actions = mapper.map_intent(
        intent
    )

    goto_actions = [
        action
        for action in actions
        if action.action_type == "goto"
    ]

    assert len(goto_actions) == 1

    assert (
        goto_actions[0].value
        == "https://example.com"
    )


def test_sign_in_label_is_preserved() -> None:
    mapper = PlaywrightActionMapper()

    intent = AutomationIntent(
        primary_action="login",
        action_label="Sign in",
    )

    actions = mapper.map_intent(
        intent
    )

    click_actions = [
        action
        for action in actions
        if action.action_type == "click"
    ]

    assert len(click_actions) == 1

    locator = click_actions[0].locator

    assert locator is not None
    assert locator.locator_type == "role"
    assert locator.value == "button"
    assert locator.role_name == "Sign in"


def test_unknown_field_is_not_invented() -> None:
    mapper = PlaywrightActionMapper()

    intent = AutomationIntent(
        fields=[
            "unknown_field",
        ],
    )

    actions = mapper.map_intent(
        intent
    )

    fill_actions = [
        action
        for action in actions
        if action.action_type == "fill"
    ]

    assert fill_actions == []