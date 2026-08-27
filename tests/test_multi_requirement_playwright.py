from src.ingestion.normalizer import (
    InputNormalizer,
)
from src.parsing.criteria_parser import (
    CriteriaParser,
)
from src.playwright.generator import (
    PlaywrightGenerator,
)
from src.scenario_expander.expander import (
    ScenarioExpander,
)


MULTI_REQUIREMENT_INPUT = """
Given user is example.com/register
When user enters John into First Name
And user enters Smith into Last Name
And user enters 123 Main Street into Address
And user enters 18001 into Zip Code
And user selects United States from Country
And user checks Remember me
Then "Registration completed" is displayed

Given user is example.com/search
When user enters Playwright into Search
And user presses Enter in Search
Then "Search results" is displayed

Given user is example.com/profile
When user uploads resume.pdf to Resume
Then "Upload successful" is displayed
"""


def build_results():
    normalizer = InputNormalizer()
    parser = CriteriaParser()
    expander = ScenarioExpander()
    playwright_generator = (
        PlaywrightGenerator()
    )

    normalized = normalizer.normalize(
        MULTI_REQUIREMENT_INPUT
    )

    parsed = parser.parse(
        normalized
    )

    test_cases = expander.generate(
        parsed
    )

    playwright_result = (
        playwright_generator.generate(
            test_cases
        )
    )

    return (
        normalized,
        parsed,
        test_cases,
        playwright_result,
    )


def test_splits_three_gherkin_requirements():
    normalized, _, _, _ = (
        build_results()
    )

    assert len(normalized) == 3

    assert [
        item.id
        for item in normalized
    ] == [
        "AC-001",
        "AC-002",
        "AC-003",
    ]


def test_generates_three_parsed_criteria():
    _, parsed, _, _ = (
        build_results()
    )

    assert len(parsed) == 3

    assert [
        item.id
        for item in parsed
    ] == [
        "AC-001",
        "AC-002",
        "AC-003",
    ]


def test_generates_nine_test_cases():
    _, _, test_cases, _ = (
        build_results()
    )

    assert len(test_cases) == 9

    requirement_ids = [
        test_case.requirement_id
        for test_case in test_cases
    ]

    assert (
        requirement_ids.count(
            "AC-001"
        )
        == 3
    )

    assert (
        requirement_ids.count(
            "AC-002"
        )
        == 3
    )

    assert (
        requirement_ids.count(
            "AC-003"
        )
        == 3
    )


def test_ac001_has_all_registration_fields():
    _, _, _, result = (
        build_results()
    )

    ac001_positive = next(
        test
        for test in result.tests
        if (
            test.requirement_id
            == "AC-001"
            and test.scenario_type
            == "Positive"
        )
    )

    locator_values = [
        action.locator.value
        for action
        in ac001_positive.actions
        if action.locator
        is not None
    ]

    assert "First Name" in locator_values
    assert "Last Name" in locator_values
    assert "Address" in locator_values
    assert "Zip Code" in locator_values
    assert "Country" in locator_values
    assert "Remember Me" in locator_values


def test_ac001_preserves_explicit_values():
    _, _, _, result = (
        build_results()
    )

    ac001_positive = next(
        test
        for test in result.tests
        if (
            test.requirement_id
            == "AC-001"
            and test.scenario_type
            == "Positive"
        )
    )

    values_by_target = {
        action.locator.value: (
            action.value
        )
        for action
        in ac001_positive.actions
        if (
            action.locator
            is not None
            and action.action_type
            == "fill"
        )
    }

    assert (
        values_by_target[
            "First Name"
        ]
        == "John"
    )

    assert (
        values_by_target[
            "Last Name"
        ]
        == "Smith"
    )

    assert (
        values_by_target[
            "Address"
        ]
        == "123 Main Street"
    )

    assert (
        values_by_target[
            "Zip Code"
        ]
        == "18001"
    )


def test_ac001_does_not_leak_other_actions():
    _, _, _, result = (
        build_results()
    )

    ac001_tests = [
        test
        for test in result.tests
        if (
            test.requirement_id
            == "AC-001"
        )
    ]

    for test in ac001_tests:
        locator_values = [
            action.locator.value
            for action in test.actions
            if action.locator
            is not None
        ]

        assert (
            "Resume"
            not in locator_values
        )

        assert (
            "Search"
            not in locator_values
        )


def test_ac002_contains_only_search_flow():
    _, _, _, result = (
        build_results()
    )

    ac002_positive = next(
        test
        for test in result.tests
        if (
            test.requirement_id
            == "AC-002"
            and test.scenario_type
            == "Positive"
        )
    )

    locator_values = [
        action.locator.value
        for action
        in ac002_positive.actions
        if action.locator
        is not None
    ]

    assert "Search" in locator_values

    assert (
        "Resume"
        not in locator_values
    )

    assert (
        "Country"
        not in locator_values
    )


def test_ac003_contains_only_upload_flow():
    _, _, _, result = (
        build_results()
    )

    ac003_positive = next(
        test
        for test in result.tests
        if (
            test.requirement_id
            == "AC-003"
            and test.scenario_type
            == "Positive"
        )
    )

    upload_actions = [
        action
        for action
        in ac003_positive.actions
        if (
            action.action_type
            == "set_input_files"
        )
    ]

    assert len(
        upload_actions
    ) == 1

    assert (
        upload_actions[0]
        .locator
        is not None
    )

    assert (
        upload_actions[0]
        .locator
        .value
        == "Resume"
    )

    assert (
        upload_actions[0].value
        == "resume.pdf"
    )


def test_all_three_requirements_reach_playwright():
    _, _, _, result = (
        build_results()
    )

    requirement_ids = {
        test.requirement_id
        for test in result.tests
    }

    assert requirement_ids == {
        "AC-001",
        "AC-002",
        "AC-003",
    }