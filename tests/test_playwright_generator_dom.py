from src.models.schemas import TestCase
from src.playwright.dom_parser import DOMParser
from src.playwright.generator import (
    PlaywrightGenerator,
)


def build_test_case(
    source_criterion: str,
) -> TestCase:
    return TestCase(
        requirement_id="AC-001",
        test_case_id="TC-001",
        test_scenario=(
            "Validate user can enter email"
        ),
        test_case_description=(
            "Validate email entry"
        ),
        preconditions=[],
        test_steps=[
            "Enter email",
        ],
        test_data="user@example.com",
        expected_result=(
            '"Email accepted" is displayed'
        ),
        scenario_type="Positive",
        priority="Medium",
        source_criterion=source_criterion,
    )


def test_generator_without_dom_uses_inferred_locator():
    test_case = build_test_case(
        """
        Given user is example.com/login
        When user enters user@example.com into Email
        Then "Email accepted" is displayed
        """
    )

    result = (
        PlaywrightGenerator()
        .generate(
            [test_case]
        )
    )

    assert (
        "page.getByLabel('Email')"
        in result.typescript_code
    )


def test_generator_uses_dom_test_id():
    test_case = build_test_case(
        """
        Given user is example.com/login
        When user enters user@example.com into Email
        Then "Email accepted" is displayed
        """
    )

    html = """
    <input
        type="email"
        data-testid="login-email"
    />
    """

    dom_elements = (
        DOMParser()
        .parse(html)
        .elements
    )

    result = (
        PlaywrightGenerator()
        .generate(
            [test_case],
            dom_elements=dom_elements,
        )
    )

    assert (
        "page.getByTestId('login-email')"
        in result.typescript_code
    )

    assert (
        "page.getByLabel('Email')"
        not in result.typescript_code
    )


def test_generator_uses_dom_label():
    test_case = build_test_case(
        """
        Given user is example.com/login
        When user enters user@example.com into Email
        Then "Email accepted" is displayed
        """
    )

    html = """
    <label for="account-email">
        Account Email
    </label>

    <input
        id="account-email"
        type="email"
        data-testid="login-email"
    />
    """

    dom_elements = (
        DOMParser()
        .parse(html)
        .elements
    )

    result = (
        PlaywrightGenerator()
        .generate(
            [test_case],
            dom_elements=dom_elements,
        )
    )

    assert (
        "page.getByLabel('Account Email')"
        in result.typescript_code
    )


def test_generator_falls_back_when_dom_does_not_match():
    test_case = build_test_case(
        """
        Given user is example.com/login
        When user enters user@example.com into Email
        Then "Email accepted" is displayed
        """
    )

    html = """
    <button>
        Cancel
    </button>
    """

    dom_elements = (
        DOMParser()
        .parse(html)
        .elements
    )

    result = (
        PlaywrightGenerator()
        .generate(
            [test_case],
            dom_elements=dom_elements,
        )
    )

    assert (
        "page.getByLabel('Email')"
        in result.typescript_code
    )