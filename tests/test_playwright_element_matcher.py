from src.playwright.dom_parser import (
    DOMParser,
)
from src.playwright.element_matcher import (
    DOMElementMatcher,
)


def build_elements():
    html = """
    <label for="email">
        Email Address
    </label>

    <input
        id="email"
        name="email"
        type="email"
        placeholder="Enter your email"
        data-testid="login-email"
    />

    <label for="country">
        Country
    </label>

    <select
        id="country"
        name="country"
    ></select>

    <label for="remember">
        Remember me
    </label>

    <input
        id="remember"
        type="checkbox"
    />

    <button
        data-testid="login-submit"
    >
        Sign In
    </button>

    <a href="/forgot-password">
        Forgot Password
    </a>
    """

    return DOMParser().parse(
        html
    ).elements


def test_matches_email_by_label() -> None:
    match = DOMElementMatcher().match(
        "Email Address",
        build_elements(),
    )

    assert match is not None

    assert (
        match.element.element_id
        == "email"
    )

    assert "label" in match.matched_by


def test_matches_email_using_short_target() -> None:
    match = DOMElementMatcher().match(
        "Email",
        build_elements(),
    )

    assert match is not None

    assert (
        match.element.element_id
        == "email"
    )


def test_matches_country() -> None:
    match = DOMElementMatcher().match(
        "Country",
        build_elements(),
    )

    assert match is not None

    assert match.element.tag == "select"

    assert (
        match.element.element_id
        == "country"
    )


def test_matches_checkbox() -> None:
    match = DOMElementMatcher().match(
        "Remember me",
        build_elements(),
        expected_type="checkbox",
    )

    assert match is not None

    assert (
        match.element.element_type
        == "checkbox"
    )


def test_matches_button_text() -> None:
    match = DOMElementMatcher().match(
        "Sign In",
        build_elements(),
        expected_tag="button",
    )

    assert match is not None

    assert match.element.tag == "button"

    assert (
        match.element.text
        == "Sign In"
    )


def test_matches_link_text() -> None:
    match = DOMElementMatcher().match(
        "Forgot Password",
        build_elements(),
        expected_tag="a",
    )

    assert match is not None

    assert match.element.tag == "a"


def test_normalizes_camel_case_name() -> None:
    html = """
    <input
        id="first-name"
        name="firstName"
    />
    """

    elements = DOMParser().parse(
        html
    ).elements

    match = DOMElementMatcher().match(
        "First Name",
        elements,
    )

    assert match is not None

    assert (
        match.element.name
        == "firstName"
    )


def test_normalizes_hyphenated_id() -> None:
    html = """
    <input
        id="zip-code"
    />
    """

    elements = DOMParser().parse(
        html
    ).elements

    match = DOMElementMatcher().match(
        "Zip Code",
        elements,
    )

    assert match is not None

    assert (
        match.element.element_id
        == "zip-code"
    )


def test_returns_none_for_unknown_target() -> None:
    match = DOMElementMatcher().match(
        "Completely Unknown Field",
        build_elements(),
    )

    assert match is None

def test_structure_alone_does_not_create_match():
    html = """
    <input
        id="completely-unrelated"
        type="email"
    />
    """

    elements = (
        DOMParser()
        .parse(html)
        .elements
    )

    match = (
        DOMElementMatcher()
        .match(
            "Account Number",
            elements,
            expected_tag="input",
        )
    )

    assert match is None    