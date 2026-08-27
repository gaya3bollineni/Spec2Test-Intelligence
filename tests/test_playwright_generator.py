from src.models.schemas import TestCase as Spec2TestCase
from src.playwright.generator import PlaywrightGenerator


def build_test_case(
    scenario_type: str = "Positive",
    expected_result: str = (
        "Verify user is redirected to home page."
    ),
    source_criterion: str | None = None,
) -> Spec2TestCase:
    return Spec2TestCase(
        test_case_id="TC-001-P1",
        requirement_id="AC-001",
        scenario_type=scenario_type,
        test_scenario=(
            "Validate user can sign in with "
            "username and password"
        ),
        test_case_description=(
            "Validate sign in using username and password."
        ),
        preconditions=[],
        test_steps=[
            "User clicks on sign in.",
            "User enters username and password.",
        ],
        test_data="Valid credentials",
        expected_result=expected_result,
        priority="Medium",
        source_criterion=(
            source_criterion
            or (
                "Given user is mail.google.com "
                "When user clicks on sign in "
                "And enters username and password "
                "Then verify user is redirected "
                "to home page"
            )
        ),
    )


def test_generator_creates_playwright_test() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [build_test_case()]
    )

    assert result.generated_test_count == 1
    assert len(result.tests) == 1


def test_generator_adds_playwright_import() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [build_test_case()]
    )

    assert (
        "import { test, expect } "
        "from '@playwright/test';"
        in result.typescript_code
    )


def test_generator_uses_requirement_url() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [build_test_case()]
    )

    assert (
        "await page.goto("
        "'https://mail.google.com');"
        in result.typescript_code
    )


def test_generator_has_only_one_goto() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [build_test_case()]
    )

    assert (
        result.typescript_code.count(
            "await page.goto("
            "'https://mail.google.com');"
        )
        == 1
    )


def test_generator_renders_username_fill() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [build_test_case()]
    )

    assert (
        "page.getByLabel('Username')"
        ".fill('test_user');"
        in result.typescript_code
    )


def test_generator_renders_password_fill() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [build_test_case()]
    )

    assert (
        "page.getByLabel('Password')"
        ".fill('TestPassword123!');"
        in result.typescript_code
    )


def test_generator_preserves_sign_in_label() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [build_test_case()]
    )

    assert (
        "page.getByRole("
        "'button', { name: 'Sign in' })"
        ".click();"
        in result.typescript_code
    )


def test_generator_creates_url_assertion() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [build_test_case()]
    )

    assert "toHaveURL" in result.typescript_code


def test_negative_test_uses_invalid_credentials() -> None:
    generator = PlaywrightGenerator()

    test_case = build_test_case(
        scenario_type="Negative",
        expected_result=(
            "System should prevent the action "
            "and display an appropriate error message."
        ),
    )

    test_case.test_case_id = "TC-001-N1"

    result = generator.generate(
        [test_case]
    )

    assert ".fill('invalid_user');" in result.typescript_code
    assert ".fill('invalid_password');" in result.typescript_code


def test_unknown_assertion_generates_safe_todo() -> None:
    generator = PlaywrightGenerator()

    test_case = build_test_case(
        expected_result=(
            "System should process the request successfully."
        )
    )

    result = generator.generate(
        [test_case]
    )

    assert (
        "// TODO: Configure "
        "application-specific assertion for:"
        in result.typescript_code
    )


def test_generator_renders_dropdown() -> None:
    generator = PlaywrightGenerator()

    test_case = build_test_case(
        source_criterion=(
            "Given user is example.com/register "
            "When user selects United States from Country "
            "Then \"Registration form\" is displayed"
        ),
        expected_result=(
            "\"Registration form\" is displayed"
        ),
    )

    result = generator.generate(
        [test_case]
    )

    assert (
        "page.getByLabel('Country')"
        ".selectOption('United States');"
        in result.typescript_code
    )


def test_generator_renders_checkbox() -> None:
    generator = PlaywrightGenerator()

    test_case = build_test_case(
        source_criterion=(
            "Given user is example.com/settings "
            "When user checks Remember me "
            "Then \"Settings saved\" is displayed"
        ),
        expected_result=(
            "\"Settings saved\" is displayed"
        ),
    )

    result = generator.generate(
        [test_case]
    )

    assert (
        "page.getByLabel('Remember Me').check();"
        in result.typescript_code
    )


def test_generator_renders_uncheck() -> None:
    generator = PlaywrightGenerator()

    test_case = build_test_case(
        source_criterion=(
            "Given user is example.com/settings "
            "When user unchecks Email notifications "
            "Then \"Settings saved\" is displayed"
        ),
        expected_result=(
            "\"Settings saved\" is displayed"
        ),
    )

    result = generator.generate(
        [test_case]
    )

    assert (
        "page.getByLabel('Email Notifications')"
        ".uncheck();"
        in result.typescript_code
    )


def test_generator_renders_radio() -> None:
    generator = PlaywrightGenerator()

    test_case = build_test_case(
        source_criterion=(
            "Given user is example.com/profile "
            "When user selects Male radio button "
            "Then \"Profile updated\" is displayed"
        ),
        expected_result=(
            "\"Profile updated\" is displayed"
        ),
    )

    result = generator.generate(
        [test_case]
    )

    assert (
        "page.getByLabel('Male').check();"
        in result.typescript_code
    )


def test_generator_renders_link() -> None:
    generator = PlaywrightGenerator()

    test_case = build_test_case(
        source_criterion=(
            "Given user is example.com/login "
            "When user clicks Forgot Password link "
            "Then \"Reset Password\" is displayed"
        ),
        expected_result=(
            "\"Reset Password\" is displayed"
        ),
    )

    result = generator.generate(
        [test_case]
    )

    assert (
        "page.getByRole("
        "'link', { name: 'Forgot Password' })"
        ".click();"
        in result.typescript_code
    )