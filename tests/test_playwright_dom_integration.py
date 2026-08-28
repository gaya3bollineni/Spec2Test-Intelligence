from src.playwright.action_mapper import (
    PlaywrightActionMapper,
)
from src.playwright.dom_parser import (
    DOMParser,
)
from src.playwright.intent import (
    AutomationIntent,
    AutomationInteraction,
)


def parse_dom(
    html: str,
):
    return DOMParser().parse(
        html
    ).elements


def test_no_dom_preserves_existing_fill_locator():
    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="fill",
                target="Email",
                value="user@example.com",
            )
        ]
    )

    actions = (
        PlaywrightActionMapper()
        .map_intent(intent)
    )

    fill = actions[1]

    assert fill.action_type == "fill"

    assert (
        fill.locator.locator_type
        == "label"
    )

    assert (
        fill.locator.value
        == "Email"
    )


def test_dom_replaces_inferred_email_locator():
    html = """
    <input
        type="email"
        data-testid="login-email"
    />
    """

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="fill",
                target="Email",
                value="user@example.com",
            )
        ]
    )

    actions = (
        PlaywrightActionMapper()
        .map_intent(
            intent,
            dom_elements=parse_dom(
                html
            ),
        )
    )

    fill = actions[1]

    assert (
        fill.locator.locator_type
        == "test_id"
    )

    assert (
        fill.locator.value
        == "login-email"
    )


def test_dom_prefers_real_label():
    html = """
    <label for="email-field">
        Email Address
    </label>

    <input
        id="email-field"
        type="email"
        data-testid="email-input"
    />
    """

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="fill",
                target="Email",
                value="user@example.com",
            )
        ]
    )

    actions = (
        PlaywrightActionMapper()
        .map_intent(
            intent,
            dom_elements=parse_dom(
                html
            ),
        )
    )

    fill = actions[1]

    assert (
        fill.locator.locator_type
        == "label"
    )

    assert (
        fill.locator.value
        == "Email Address"
    )


def test_dom_matches_select():
    html = """
    <select
        id="country-select"
        data-testid="country-dropdown"
        aria-label="Country"
    >
        <option value="US">
            United States
        </option>
    </select>
    """

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="select",
                target="Country",
                value="United States",
            )
        ]
    )

    actions = (
        PlaywrightActionMapper()
        .map_intent(
            intent,
            dom_elements=parse_dom(
                html
            ),
        )
    )

    select = actions[1]

    assert select.action_type == "select"

    assert (
        select.locator.locator_type
        == "label"
    )

    assert (
        select.locator.value
        == "Country"
    )


def test_dom_matches_checkbox():
    html = """
    <input
        id="remember-option"
        type="checkbox"
        data-testid="remember-checkbox"
        aria-label="Remember me"
    />
    """

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="check",
                target="Remember Me",
            )
        ]
    )

    actions = (
        PlaywrightActionMapper()
        .map_intent(
            intent,
            dom_elements=parse_dom(
                html
            ),
        )
    )

    check = actions[1]

    assert check.action_type == "check"

    assert (
        check.locator.locator_type
        == "label"
    )

    assert (
        check.locator.value
        == "Remember me"
    )


def test_dom_matches_file_upload():
    html = """
    <input
        id="resume-upload"
        type="file"
        data-testid="resume-file"
    />
    """

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="upload",
                target="Resume",
                value="resume.pdf",
            )
        ]
    )

    actions = (
        PlaywrightActionMapper()
        .map_intent(
            intent,
            dom_elements=parse_dom(
                html
            ),
        )
    )

    upload = actions[1]

    assert (
        upload.action_type
        == "set_input_files"
    )

    assert (
        upload.locator.locator_type
        == "test_id"
    )

    assert (
        upload.locator.value
        == "resume-file"
    )


def test_dom_matches_link():
    html = """
    <a
        href="/forgot-password"
        data-testid="forgot-link"
    >
        Forgot Password
    </a>
    """

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="link",
                target="Forgot Password",
            )
        ]
    )

    actions = (
        PlaywrightActionMapper()
        .map_intent(
            intent,
            dom_elements=parse_dom(
                html
            ),
        )
    )

    click = actions[1]

    assert click.action_type == "click"

    assert (
        click.locator.locator_type
        == "role"
    )

    assert click.locator.value == "link"

    assert (
        click.locator.role_name
        == "Forgot Password"
    )


def test_dom_matches_primary_button():
    html = """
    <button
        id="signin"
        data-testid="signin-button"
    >
        Sign In
    </button>
    """

    intent = AutomationIntent(
        primary_action="login",
        action_label="Sign In",
    )

    actions = (
        PlaywrightActionMapper()
        .map_intent(
            intent,
            dom_elements=parse_dom(
                html
            ),
        )
    )

    click = actions[1]

    assert click.action_type == "click"

    assert (
        click.locator.locator_type
        == "role"
    )

    assert click.locator.value == "button"

    assert (
        click.locator.role_name
        == "Sign In"
    )


def test_unknown_dom_target_falls_back():
    html = """
    <button>
        Completely Different Action
    </button>
    """

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="fill",
                target="Email",
                value="user@example.com",
            )
        ]
    )

    actions = (
        PlaywrightActionMapper()
        .map_intent(
            intent,
            dom_elements=parse_dom(
                html
            ),
        )
    )

    fill = actions[1]

    assert (
        fill.locator.locator_type
        == "label"
    )

    assert (
        fill.locator.value
        == "Email"
    )


def test_dom_matches_press_target():
    html = """
    <input
        type="search"
        data-testid="product-search"
        aria-label="Search"
    />
    """

    intent = AutomationIntent(
        interactions=[
            AutomationInteraction(
                interaction_type="press",
                target="Search",
                value="Enter",
            )
        ]
    )

    actions = (
        PlaywrightActionMapper()
        .map_intent(
            intent,
            dom_elements=parse_dom(
                html
            ),
        )
    )

    press = actions[1]

    assert press.action_type == "press"

    assert (
        press.locator.locator_type
        == "label"
    )

    assert (
        press.locator.value
        == "Search"
    )