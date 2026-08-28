from src.playwright.dom_models import (
    DOMElement,
)
from src.playwright.locator_generator import (
    DOMLocatorGenerator,
)


def test_button_prefers_role_locator() -> None:
    element = DOMElement(
        tag="button",
        text="Sign In",
        test_id="login-submit",
    )

    locator = (
        DOMLocatorGenerator()
        .generate(element)
    )

    assert locator is not None

    assert (
        locator.locator_type
        == "role"
    )

    assert locator.value == "button"

    assert (
        locator.role_name
        == "Sign In"
    )


def test_link_prefers_role_locator() -> None:
    element = DOMElement(
        tag="a",
        text="Forgot Password",
        href="/forgot-password",
    )

    locator = (
        DOMLocatorGenerator()
        .generate(element)
    )

    assert locator is not None

    assert (
        locator.locator_type
        == "role"
    )

    assert locator.value == "link"

    assert (
        locator.role_name
        == "Forgot Password"
    )


def test_form_control_prefers_label() -> None:
    element = DOMElement(
        tag="input",
        element_type="email",
        label="Email Address",
        test_id="login-email",
        placeholder="Enter your email",
    )

    locator = (
        DOMLocatorGenerator()
        .generate(element)
    )

    assert locator is not None

    assert (
        locator.locator_type
        == "label"
    )

    assert (
        locator.value
        == "Email Address"
    )


def test_test_id_used_without_label() -> None:
    element = DOMElement(
        tag="input",
        element_type="email",
        test_id="login-email",
        placeholder="Enter your email",
    )

    locator = (
        DOMLocatorGenerator()
        .generate(element)
    )

    assert locator is not None

    assert (
        locator.locator_type
        == "test_id"
    )

    assert (
        locator.value
        == "login-email"
    )


def test_placeholder_used_without_test_id() -> None:
    element = DOMElement(
        tag="input",
        placeholder="Search products",
    )

    locator = (
        DOMLocatorGenerator()
        .generate(element)
    )

    assert locator is not None

    assert (
        locator.locator_type
        == "placeholder"
    )

    assert (
        locator.value
        == "Search products"
    )


def test_id_used_as_css_fallback() -> None:
    element = DOMElement(
        tag="input",
        element_id="username",
    )

    locator = (
        DOMLocatorGenerator()
        .generate(element)
    )

    assert locator is not None

    assert (
        locator.locator_type
        == "css"
    )

    assert (
        locator.value
        == "#username"
    )


def test_name_used_as_final_fallback() -> None:
    element = DOMElement(
        tag="input",
        name="accountEmail",
    )

    locator = (
        DOMLocatorGenerator()
        .generate(element)
    )

    assert locator is not None

    assert (
        locator.locator_type
        == "css"
    )

    assert (
        locator.value
        == '[name="accountEmail"]'
    )


def test_returns_none_without_locator_data() -> None:
    element = DOMElement(
        tag="input",
    )

    locator = (
        DOMLocatorGenerator()
        .generate(element)
    )

    assert locator is None


def test_checkbox_with_label_uses_label() -> None:
    element = DOMElement(
        tag="input",
        element_type="checkbox",
        label="Remember me",
        element_id="remember",
    )

    locator = (
        DOMLocatorGenerator()
        .generate(element)
    )

    assert locator is not None

    assert (
        locator.locator_type
        == "label"
    )

    assert (
        locator.value
        == "Remember me"
    )


def test_explicit_role_is_respected() -> None:
    element = DOMElement(
        tag="div",
        role="button",
        aria_label="Open menu",
    )

    locator = (
        DOMLocatorGenerator()
        .generate(element)
    )

    assert locator is not None

    assert (
        locator.locator_type
        == "role"
    )

    assert locator.value == "button"

    assert (
        locator.role_name
        == "Open menu"
    )