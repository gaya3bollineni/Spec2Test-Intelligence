from src.models.schemas import TestCase as Spec2TestCase
from src.playwright.action_mapper import PlaywrightActionMapper
from src.playwright.intent import AutomationIntent, AutomationInteraction


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
    assert actions[0].value == "https://mail.google.com"

    assert actions[1].action_type == "fill"
    assert actions[1].locator is not None
    assert actions[1].locator.value == "Username"
    assert actions[1].value == "test_user"

    assert actions[2].action_type == "fill"
    assert actions[2].locator is not None
    assert actions[2].locator.value == "Password"
    assert actions[2].value == "TestPassword123!"

    assert actions[3].action_type == "click"
    assert actions[3].locator is not None
    assert actions[3].locator.value == "button"
    assert actions[3].locator.role_name == "Sign in"


def test_negative_login_uses_invalid_values() -> None:
    mapper = PlaywrightActionMapper()

    test_case = build_test_case(
        scenario_type="Negative"
    )

    test_case.test_case_id = "TC-001-N1"

    actions = mapper.map_test_case(
        test_case
    )

    assert actions[1].value == "invalid_user"
    assert actions[2].value == "invalid_password"


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
    assert goto_actions[0].value == "https://example.com"


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


def test_maps_dropdown_interaction() -> None:
    mapper = PlaywrightActionMapper()

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="select",
                target="Country",
                value="United States",
            )
        ]
    )

    actions = mapper.map_intent(
        intent
    )

    select_actions = [
        action
        for action in actions
        if action.action_type == "select"
    ]

    assert len(select_actions) == 1

    action = select_actions[0]

    assert action.locator is not None
    assert action.locator.locator_type == "label"
    assert action.locator.value == "Country"
    assert action.value == "United States"


def test_maps_checkbox_interaction() -> None:
    mapper = PlaywrightActionMapper()

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="check",
                target="Remember Me",
            )
        ]
    )

    actions = mapper.map_intent(
        intent
    )

    check_actions = [
        action
        for action in actions
        if action.action_type == "check"
    ]

    assert len(check_actions) == 1
    assert check_actions[0].locator is not None
    assert check_actions[0].locator.value == "Remember Me"


def test_maps_uncheck_interaction() -> None:
    mapper = PlaywrightActionMapper()

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="uncheck",
                target="Email Notifications",
            )
        ]
    )

    actions = mapper.map_intent(
        intent
    )

    uncheck_actions = [
        action
        for action in actions
        if action.action_type == "uncheck"
    ]

    assert len(uncheck_actions) == 1
    assert uncheck_actions[0].locator is not None
    assert (
        uncheck_actions[0].locator.value
        == "Email Notifications"
    )


def test_maps_radio_interaction() -> None:
    mapper = PlaywrightActionMapper()

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="radio",
                target="Male",
            )
        ]
    )

    actions = mapper.map_intent(
        intent
    )

    check_actions = [
        action
        for action in actions
        if action.action_type == "check"
    ]

    assert len(check_actions) == 1
    assert check_actions[0].locator is not None
    assert check_actions[0].locator.value == "Male"


def test_maps_link_interaction() -> None:
    mapper = PlaywrightActionMapper()

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="link",
                target="Forgot Password",
            )
        ]
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
    assert locator.value == "link"
    assert locator.role_name == "Forgot Password"