from src.models.schemas import TestCase as Spec2TestCase
from src.playwright.generator import PlaywrightGenerator


def build_test_case(
    scenario_type: str = "Positive",
    expected_result: str = (
        "Verify user is redirected to home page."
    ),
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
            "Validate sign in using username "
            "and password."
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
            "Given user is mail.google.com "
            "When user clicks on sign in "
            "And enters username and password "
            "Then verify user is redirected "
            "to home page"
        ),
    )


def test_generator_creates_playwright_test() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [build_test_case()]
    )

    assert result.generated_test_count == 1
    assert len(result.tests) == 1

    generated_test = result.tests[0]

    assert generated_test.requirement_id == "AC-001"
    assert generated_test.test_case_id == "TC-001-P1"
    assert generated_test.priority == "Medium"


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

    assert (
        "await expect(page)"
        ".toHaveURL(/\\/home/);"
        in result.typescript_code
    )


def test_generator_handles_redirect_typo() -> None:
    generator = PlaywrightGenerator()

    test_case = build_test_case(
        expected_result=(
            "Verify user is recirected "
            "to home page."
        )
    )

    result = generator.generate(
        [test_case]
    )

    assert (
        "await expect(page)"
        ".toHaveURL(/\\/home/);"
        in result.typescript_code
    )


def test_generator_preserves_traceability() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [build_test_case()]
    )

    code = result.typescript_code

    assert "// Requirement: AC-001" in code
    assert "TC-001-P1" in code
    assert "// Scenario: Positive" in code
    assert "// Priority: Medium" in code


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

    code = result.typescript_code

    assert (
        ".fill('invalid_user');"
        in code
    )

    assert (
        ".fill('invalid_password');"
        in code
    )


def test_unknown_assertion_generates_safe_todo() -> None:
    generator = PlaywrightGenerator()

    test_case = build_test_case(
        expected_result=(
            "System should process the "
            "request successfully."
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


def test_generator_handles_multiple_tests() -> None:
    generator = PlaywrightGenerator()

    positive = build_test_case()

    negative = build_test_case(
        scenario_type="Negative",
        expected_result=(
            "System should display an error."
        ),
    )

    negative.test_case_id = "TC-001-N1"

    result = generator.generate(
        [
            positive,
            negative,
        ]
    )

    assert result.generated_test_count == 2
    assert len(result.tests) == 2

    assert "TC-001-P1" in result.typescript_code
    assert "TC-001-N1" in result.typescript_code