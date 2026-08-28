from src.playwright.dom_parser import (
    DOMParser,
)


def test_parses_labeled_email_input() -> None:
    html = """
    <html>
        <body>
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
        </body>
    </html>
    """

    result = DOMParser().parse(
        html
    )

    assert (
        result.interactive_element_count
        == 1
    )

    element = result.elements[0]

    assert element.tag == "input"
    assert element.element_type == "email"
    assert element.element_id == "email"
    assert element.name == "email"
    assert (
        element.label
        == "Email Address"
    )
    assert (
        element.placeholder
        == "Enter your email"
    )
    assert (
        element.test_id
        == "login-email"
    )


def test_parses_button_text() -> None:
    html = """
    <button
        data-testid="login-submit"
    >
        Sign In
    </button>
    """

    result = DOMParser().parse(
        html
    )

    assert (
        result.interactive_element_count
        == 1
    )

    button = result.elements[0]

    assert button.tag == "button"
    assert button.text == "Sign In"
    assert (
        button.test_id
        == "login-submit"
    )


def test_parses_registration_controls() -> None:
    html = """
    <label for="first-name">
        First Name
    </label>

    <input
        id="first-name"
        name="firstName"
        type="text"
    />

    <label for="country">
        Country
    </label>

    <select
        id="country"
        name="country"
    >
        <option value="US">
            United States
        </option>
    </select>

    <label for="remember">
        Remember me
    </label>

    <input
        id="remember"
        type="checkbox"
    />
    """

    result = DOMParser().parse(
        html
    )

    assert (
        result.interactive_element_count
        == 3
    )

    first_name = result.elements[0]
    country = result.elements[1]
    remember = result.elements[2]

    assert (
        first_name.label
        == "First Name"
    )

    assert country.tag == "select"
    assert country.label == "Country"

    assert (
        remember.element_type
        == "checkbox"
    )

    assert (
        remember.label
        == "Remember me"
    )


def test_parses_radio_button() -> None:
    html = """
    <label for="premium">
        Premium
    </label>

    <input
        id="premium"
        type="radio"
        name="plan"
        value="premium"
    />
    """

    result = DOMParser().parse(
        html
    )

    radio = result.elements[0]

    assert (
        radio.element_type
        == "radio"
    )

    assert radio.name == "plan"
    assert radio.value == "premium"
    assert radio.label == "Premium"


def test_parses_search_input() -> None:
    html = """
    <input
        id="search-box"
        type="search"
        name="search"
        placeholder="Search products"
        aria-label="Search"
    />
    """

    result = DOMParser().parse(
        html
    )

    search = result.elements[0]

    assert (
        search.element_type
        == "search"
    )

    assert (
        search.placeholder
        == "Search products"
    )

    assert search.label == "Search"


def test_parses_file_upload() -> None:
    html = """
    <label for="resume">
        Resume
    </label>

    <input
        id="resume"
        name="resume"
        type="file"
        data-testid="resume-upload"
    />
    """

    result = DOMParser().parse(
        html
    )

    upload = result.elements[0]

    assert (
        upload.element_type
        == "file"
    )

    assert upload.label == "Resume"

    assert (
        upload.test_id
        == "resume-upload"
    )


def test_parses_link() -> None:
    html = """
    <a
        href="/forgot-password"
        data-testid="forgot-password"
    >
        Forgot Password
    </a>
    """

    result = DOMParser().parse(
        html
    )

    link = result.elements[0]

    assert link.tag == "a"

    assert (
        link.href
        == "/forgot-password"
    )

    assert (
        link.text
        == "Forgot Password"
    )


def test_preserves_css_classes() -> None:
    html = """
    <button
        id="submit"
        class="btn btn-primary submit-button"
    >
        Submit
    </button>
    """

    result = DOMParser().parse(
        html
    )

    button = result.elements[0]

    assert button.classes == [
        "btn",
        "btn-primary",
        "submit-button",
    ]


def test_supports_alternative_test_id_attributes() -> None:
    html = """
    <input
        id="username"
        data-cy="username-input"
    />
    """

    result = DOMParser().parse(
        html
    )

    assert (
        result.elements[0].test_id
        == "username-input"
    )


def test_ignores_non_interactive_elements() -> None:
    html = """
    <div>
        Container
    </div>

    <p>
        Description
    </p>

    <span>
        Status
    </span>
    """

    result = DOMParser().parse(
        html
    )

    assert (
        result.interactive_element_count
        == 0
    )

    assert (
        "No supported interactive elements "
        "were found."
        in result.warnings
    )


def test_empty_html_returns_warning() -> None:
    result = DOMParser().parse(
        ""
    )

    assert (
        result.interactive_element_count
        == 0
    )

    assert result.elements == []

    assert (
        "No HTML content was provided."
        in result.warnings
    )


def test_parses_multiple_interactive_elements() -> None:
    html = """
    <input
        id="username"
        placeholder="Username"
    />

    <input
        id="password"
        type="password"
        placeholder="Password"
    />

    <button>
        Sign In
    </button>

    <a href="/register">
        Register
    </a>
    """

    result = DOMParser().parse(
        html
    )

    assert (
        result.interactive_element_count
        == 4
    )

    assert [
        element.tag
        for element in result.elements
    ] == [
        "input",
        "input",
        "button",
        "a",
    ]