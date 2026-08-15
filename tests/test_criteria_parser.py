from src.models.schemas import RequirementItem
from src.parsing.criteria_parser import CriteriaParser


def build_requirement(
    text: str,
    requirement_id: str = "AC-001",
) -> RequirementItem:
    return RequirementItem(
        id=requirement_id,
        raw_text=text,
        normalized_text=" ".join(text.split()),
        priority="Medium",
    )


def test_standard_gherkin_parsing() -> None:
    parser = CriteriaParser()

    requirement = build_requirement(
        """
        Given user is on the login page
        When user enters valid credentials
        Then user should see the home page
        """
    )

    parsed = parser.parse_item(requirement)

    assert parsed.actor == "user"
    assert parsed.condition is not None
    assert "login page" in parsed.condition.lower()
    assert parsed.action is not None
    assert "valid credentials" in parsed.action.lower()
    assert parsed.expected_outcome is not None
    assert "home page" in parsed.expected_outcome.lower()


def test_plain_text_requirement_parsing() -> None:
    parser = CriteriaParser()

    requirement = build_requirement(
        "User should be able to log in with valid credentials."
    )

    parsed = parser.parse_item(requirement)

    assert parsed.actor == "user"
    assert parsed.action is not None
    assert parsed.expected_outcome is not None


def test_parser_preserves_requirement_id() -> None:
    parser = CriteriaParser()

    requirement = build_requirement(
        "User can reset password.",
        requirement_id="REQ-500",
    )

    parsed = parser.parse_item(requirement)

    assert parsed.id == "REQ-500"


def test_parser_preserves_priority() -> None:
    parser = CriteriaParser()

    requirement = RequirementItem(
        id="REQ-501",
        raw_text="User can log in.",
        normalized_text="User can log in.",
        priority="Critical",
    )

    parsed = parser.parse_item(requirement)

    assert parsed.priority == "Critical"


def test_loose_gherkin_parsing() -> None:
    """
    This test represents acceptance criteria that are written
    conversationally instead of using strict Given/When/Then.
    """

    parser = CriteriaParser()

    requirement = build_requirement(
        """
        Given user is on login
        and user enter valid credentials and password
        they verify user is logged in
        and can see home page
        """
    )

    parsed = parser.parse_item(requirement)

    assert parsed.actor == "user"

    assert parsed.condition is not None
    assert "login" in parsed.condition.lower()

    assert parsed.action is not None
    assert (
        "credential" in parsed.action.lower()
        or "password" in parsed.action.lower()
    )

    assert parsed.expected_outcome is not None
    assert (
        "logged in" in parsed.expected_outcome.lower()
        or "home page" in parsed.expected_outcome.lower()
    )