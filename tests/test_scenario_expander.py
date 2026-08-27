from src.models.schemas import ParsedCriterion
from src.scenario_expander.expander import (
    ScenarioExpander,
)


def build_parsed_criterion(
    requirement_id: str = "REQ-101",
    priority: str = "High",
) -> ParsedCriterion:
    return ParsedCriterion(
        id=requirement_id,
        raw_text=(
            "User can log in with valid credentials."
        ),
        actor="user",
        action="log in",
        condition="with valid credentials",
        expected_outcome=(
            "User can log in with valid credentials."
        ),
        rule_type="functional",
        priority=priority,
    )


def test_high_priority_generates_four_scenario_types() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        priority="High"
    )

    test_cases = expander.generate(
        [criterion]
    )

    assert len(test_cases) == 4

    assert [
        test_case.scenario_type
        for test_case in test_cases
    ] == [
        "Positive",
        "Negative",
        "Edge",
        "Boundary",
    ]


def test_expander_preserves_requirement_id() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        requirement_id="REQ-999"
    )

    test_cases = expander.generate(
        [criterion]
    )

    assert all(
        test_case.requirement_id == "REQ-999"
        for test_case in test_cases
    )


def test_expander_preserves_uploaded_priority() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        priority="Critical"
    )

    test_cases = expander.generate(
        [criterion]
    )

    assert len(test_cases) == 5

    assert all(
        test_case.priority == "Critical"
        for test_case in test_cases
    )


def test_expander_defaults_invalid_priority_to_medium() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        priority="Urgent"
    )

    test_cases = expander.generate(
        [criterion]
    )

    assert len(test_cases) == 3

    assert all(
        test_case.priority == "Medium"
        for test_case in test_cases
    )

    assert [
        test_case.scenario_type
        for test_case in test_cases
    ] == [
        "Positive",
        "Negative",
        "Edge",
    ]


def test_expander_generates_unique_test_case_ids() -> None:
    expander = ScenarioExpander()

    criteria = [
        build_parsed_criterion(
            requirement_id="REQ-101",
            priority="High",
        ),
        build_parsed_criterion(
            requirement_id="REQ-102",
            priority="High",
        ),
    ]

    test_cases = expander.generate(
        criteria
    )

    test_case_ids = [
        test_case.test_case_id
        for test_case in test_cases
    ]

    assert len(test_case_ids) == len(
        set(test_case_ids)
    )

    assert test_case_ids == [
        "TC-001-P1",
        "TC-001-N1",
        "TC-001-E1",
        "TC-001-B1",
        "TC-002-P1",
        "TC-002-N1",
        "TC-002-E1",
        "TC-002-B1",
    ]


def test_low_priority_generates_two_cases() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        priority="Low"
    )

    test_cases = expander.generate(
        [criterion]
    )

    assert len(test_cases) == 2

    assert [
        test_case.scenario_type
        for test_case in test_cases
    ] == [
        "Positive",
        "Negative",
    ]


def test_medium_priority_generates_three_cases() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        priority="Medium"
    )

    test_cases = expander.generate(
        [criterion]
    )

    assert len(test_cases) == 3

    assert [
        test_case.scenario_type
        for test_case in test_cases
    ] == [
        "Positive",
        "Negative",
        "Edge",
    ]


def test_high_priority_generates_four_cases() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        priority="High"
    )

    test_cases = expander.generate(
        [criterion]
    )

    assert len(test_cases) == 4


def test_critical_priority_generates_five_cases() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        priority="Critical"
    )

    test_cases = expander.generate(
        [criterion]
    )

    assert len(test_cases) == 5

    scenario_types = {
        test_case.scenario_type
        for test_case in test_cases
    }

    assert scenario_types == {
        "Positive",
        "Negative",
        "Edge",
        "Boundary",
        "Security",
    }


def test_boundary_scenario_has_boundary_test_data() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        priority="High"
    )

    test_cases = expander.generate(
        [criterion]
    )

    boundary_test = next(
        test_case
        for test_case in test_cases
        if test_case.scenario_type == "Boundary"
    )

    assert "minimum" in (
        boundary_test.test_data.lower()
    )

    assert "maximum" in (
        boundary_test.test_data.lower()
    )


def test_security_scenario_generated_for_critical_requirement() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        priority="Critical"
    )

    test_cases = expander.generate(
        [criterion]
    )

    security_test = next(
        test_case
        for test_case in test_cases
        if test_case.scenario_type == "Security"
    )

    assert security_test.priority == "Critical"

    assert "unauthorized" in (
        security_test.test_data.lower()
    )

def test_normalizes_conversational_action_for_title() -> None:
    expander = ScenarioExpander()

    result = expander.normalize_action_for_title(
        "user clicks on sign in And enters username and password"
    )

    assert (
        result
        == "sign in with username and password"
    )


def test_generated_title_avoids_duplicate_actor_wording() -> None:
    expander = ScenarioExpander()

    criterion = build_parsed_criterion(
        priority="Medium"
    )

    criterion.actor = "user"

    criterion.action = (
        "user clicks on sign in "
        "And enters username and password"
    )

    test_cases = expander.generate(
        [criterion]
    )

    assert (
        test_cases[0].test_scenario
        == (
            "Validate user can sign in with "
            "username and password successfully"
        )
    )    