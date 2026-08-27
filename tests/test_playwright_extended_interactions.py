from src.models.schemas import TestCase as Spec2TestCase
from src.playwright.generator import PlaywrightGenerator


def build_test_case(
    source_criterion: str,
) -> Spec2TestCase:
    return Spec2TestCase(
        test_case_id="TC-001-P1",
        requirement_id="AC-001",
        scenario_type="Positive",
        test_scenario="Validate UI interaction",
        test_case_description=source_criterion,
        preconditions=[],
        test_steps=[],
        test_data="Valid input data",
        expected_result=(
            '"Action completed" is displayed'
        ),
        priority="Medium",
        source_criterion=source_criterion,
    )


def test_general_address_field() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [
            build_test_case(
                "Given user is example.com/profile "
                "When user enters 123 Main Street "
                "into Address "
                'Then "Action completed" is displayed'
            )
        ]
    )

    assert (
        "page.getByLabel('Address')"
        ".fill('123 Main Street');"
        in result.typescript_code
    )


def test_general_zip_code_field() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [
            build_test_case(
                "Given user is example.com/profile "
                "When user enters 18001 into Zip Code "
                'Then "Action completed" is displayed'
            )
        ]
    )

    assert (
        "page.getByLabel('Zip Code')"
        ".fill('18001');"
        in result.typescript_code
    )


def test_keyboard_enter() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [
            build_test_case(
                "Given user is example.com/search "
                "When user presses Enter in Search "
                'Then "Action completed" is displayed'
            )
        ]
    )

    assert (
        "page.getByLabel('Search')"
        ".press('Enter');"
        in result.typescript_code
    )


def test_file_upload() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [
            build_test_case(
                "Given user is example.com/profile "
                "When user uploads resume.pdf to Resume "
                'Then "Action completed" is displayed'
            )
        ]
    )

    assert (
        "page.getByLabel('Resume')"
        ".setInputFiles('resume.pdf');"
        in result.typescript_code
    )


def test_existing_dropdown_still_works() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [
            build_test_case(
                "Given user is example.com/register "
                "When user selects United States from Country "
                'Then "Action completed" is displayed'
            )
        ]
    )

    assert (
        "page.getByLabel('Country')"
        ".selectOption('United States');"
        in result.typescript_code
    )


def test_existing_checkbox_still_works() -> None:
    generator = PlaywrightGenerator()

    result = generator.generate(
        [
            build_test_case(
                "Given user is example.com/settings "
                "When user checks Remember me "
                'Then "Action completed" is displayed'
            )
        ]
    )

    assert (
        "page.getByLabel('Remember Me').check();"
        in result.typescript_code
    )