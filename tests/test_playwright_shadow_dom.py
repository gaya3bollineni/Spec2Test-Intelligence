from src.models.schemas import (
    TestCase as Spec2TestCase,
)
from src.playwright.dom_parser import DOMParser
from src.playwright.generator import (
    PlaywrightGenerator,
)


def build_test_case(
    source_criterion: str,
) -> Spec2TestCase:
    return Spec2TestCase(
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


def test_generator_uses_label_inside_shadow_dom():
    test_case = build_test_case(
        """
        Given user is example.com/login
        When user enters user@example.com into Email
        Then "Email accepted" is displayed
        """
    )

    html = """
    <user-login>
        <template shadowrootmode="open">

            <label for="email">
                Email
            </label>

            <input
                id="email"
                type="email"
            />

        </template>
    </user-login>
    """

    parse_result = (
        DOMParser()
        .parse(html)
    )

    shadow_elements = [
        element
        for element in parse_result.elements
        if element.inside_shadow_dom
    ]

    assert len(shadow_elements) == 1

    email_element = shadow_elements[0]

    assert email_element.tag == "input"
    assert email_element.label == "Email"
    assert (
        email_element.inside_shadow_dom
        is True
    )
    assert email_element.shadow_host_path

    result = (
        PlaywrightGenerator()
        .generate(
            [test_case],
            dom_elements=parse_result.elements,
        )
    )

    assert (
        "page.getByLabel('Email')"
        in result.typescript_code
    )


def test_generator_uses_test_id_inside_shadow_dom():
    test_case = build_test_case(
        """
        Given user is example.com/login
        When user enters user@example.com into Email
        Then "Email accepted" is displayed
        """
    )

    html = """
    <user-login>
        <template shadowrootmode="open">

            <input
                type="email"
                data-testid="shadow-email"
            />

        </template>
    </user-login>
    """

    parse_result = (
        DOMParser()
        .parse(html)
    )

    assert len(
        parse_result.elements
    ) == 1

    email_element = (
        parse_result.elements[0]
    )

    assert (
        email_element.inside_shadow_dom
        is True
    )

    result = (
        PlaywrightGenerator()
        .generate(
            [test_case],
            dom_elements=parse_result.elements,
        )
    )

    assert (
        "page.getByTestId('shadow-email')"
        in result.typescript_code
    )


def test_generator_handles_nested_shadow_dom():
    test_case = build_test_case(
        """
        Given user is example.com/login
        When user enters user@example.com into Email
        Then "Email accepted" is displayed
        """
    )

    html = """
    <application-shell>
        <template shadowrootmode="open">

            <login-form>
                <template shadowrootmode="open">

                    <label for="email">
                        Email
                    </label>

                    <input
                        id="email"
                        type="email"
                    />

                </template>
            </login-form>

        </template>
    </application-shell>
    """

    parse_result = (
        DOMParser()
        .parse(html)
    )

    assert len(
        parse_result.elements
    ) == 1

    email_element = (
        parse_result.elements[0]
    )

    assert (
        email_element.inside_shadow_dom
        is True
    )

    assert len(
        email_element.shadow_host_path
    ) == 2

    result = (
        PlaywrightGenerator()
        .generate(
            [test_case],
            dom_elements=parse_result.elements,
        )
    )

    assert (
        "page.getByLabel('Email')"
        in result.typescript_code
    )