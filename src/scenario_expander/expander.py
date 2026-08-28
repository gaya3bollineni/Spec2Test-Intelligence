import re
from typing import List

from src.models.schemas import ParsedCriterion, TestCase
from src.oracle_builder.expected_result_builder import (
    ExpectedResultBuilder,
)


class ScenarioExpander:
    def __init__(self) -> None:
        self.expected_builder = ExpectedResultBuilder()

    def build_title(
        self,
        criterion: ParsedCriterion,
        scenario_type: str,
    ) -> str:
        actor = self.normalize_actor_for_title(
            criterion.actor
        )

        action = self.normalize_action_for_title(
            criterion.action
        )

        titles = {
            "Positive": (
                f"Validate {actor} can {action} successfully"
            ),
            "Negative": (
                f"Validate {actor} cannot {action} "
                "with invalid input"
            ),
            "Edge": (
                f"Validate edge behavior when {actor} "
                f"attempts to {action}"
            ),
            "Boundary": (
                f"Validate boundary values when {actor} "
                f"attempts to {action}"
            ),
            "Security": (
                f"Validate unauthorized or restricted "
                f"behavior when {actor} attempts to {action}"
            ),
        }

        return titles.get(
            scenario_type,
            f"Validate {actor} can {action}",
        )

    @staticmethod
    def normalize_actor_for_title(
        actor: str | None,
    ) -> str:
        if not actor:
            return "user"

        cleaned = re.sub(
            r"\s+",
            " ",
            actor.strip(),
        ).strip(" .")

        if not cleaned:
            return "user"

        return cleaned.lower()

    @staticmethod
    def normalize_action_for_title(
        action: str | None,
    ) -> str:
        """
        Converts conversational parser output into a concise,
        readable scenario-title action.

        Examples:

        "user clicks on sign in And enters username and password"
        -> "sign in with username and password"

        "user enters John into First Name And user enters Smith
        into Last Name And user enters 123 Main Street into Address"
        -> "complete the form"

        "user enters Playwright into Search And user presses Enter
        in Search"
        -> "search using Playwright"

        "user uploads resume.pdf to Resume"
        -> "upload resume.pdf to Resume"
        """

        if not action:
            return "perform the requested action"

        cleaned = re.sub(
            r"\s+",
            " ",
            action.strip(),
        ).strip(" .")

        # Remove repeated actor prefixes throughout the action.
        cleaned = re.sub(
            r"^(?:the\s+)?"
            r"(?:user|customer|admin|agent|guest)\s+",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s+[Aa]nd\s+(?:the\s+)?"
            r"(?:user|customer|admin|agent|guest)\s+",
            " and ",
            cleaned,
            flags=re.IGNORECASE,
        )

        # ---------------------------------------------------------
        # LOGIN / SIGN-IN
        # ---------------------------------------------------------

        login_match = re.match(
            r"(?:clicks?\s+(?:on\s+)?)?"
            r"(sign[\s-]?in|log[\s-]?in|login)"
            r"\s+and\s+enters?\s+(.+)$",
            cleaned,
            flags=re.IGNORECASE,
        )

        if login_match:
            credentials = login_match.group(2).strip()

            return (
                f"sign in with {credentials}"
            ).lower()

        # ---------------------------------------------------------
        # SEARCH
        # ---------------------------------------------------------

        search_match = re.search(
            r"enters?\s+(.+?)\s+into\s+search"
            r"(?:\s+and\s+press(?:es)?\s+enter"
            r"(?:\s+in\s+search)?)?",
            cleaned,
            flags=re.IGNORECASE,
        )

        if search_match:
            search_value = (
                search_match.group(1)
                .strip(" .")
            )

            return (
                f"search using {search_value}"
            )

        # ---------------------------------------------------------
        # FILE UPLOAD
        # ---------------------------------------------------------

        upload_match = re.search(
            r"uploads?\s+(.+?)\s+to\s+(.+)$",
            cleaned,
            flags=re.IGNORECASE,
        )

        if upload_match:
            file_name = (
                upload_match.group(1)
                .strip(" .")
            )

            target = (
                upload_match.group(2)
                .strip(" .")
            )

            return (
                f"upload {file_name} to {target}"
            )

        # ---------------------------------------------------------
        # MULTI-FIELD FORM
        # ---------------------------------------------------------

        field_entry_count = len(
            re.findall(
                r"\b(?:enter|enters|fill|fills|type|types)\b"
                r".+?\b(?:into|in)\b",
                cleaned,
                flags=re.IGNORECASE,
            )
        )

        has_form_interaction = bool(
            re.search(
                r"\b(?:select|selects|check|checks|"
                r"uncheck|unchecks|choose|chooses)\b",
                cleaned,
                flags=re.IGNORECASE,
            )
        )

        if (
            field_entry_count >= 2
            or (
                field_entry_count >= 1
                and has_form_interaction
            )
        ):
            return "complete the form"

        # ---------------------------------------------------------
        # GENERAL CLEANUP
        # ---------------------------------------------------------

        cleaned = re.sub(
            r"^clicks?\s+on\s+",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"^clicks?\s+",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"^enters\b",
            "enter",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"^fills\b",
            "fill",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"^selects\b",
            "select",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"^checks\b",
            "check",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"^unchecks\b",
            "uncheck",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"^uploads\b",
            "upload",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"^presses\b",
            "press",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        ).strip(" .")

        if not cleaned:
            return "perform the requested action"

        return cleaned

    def build_steps(
        self,
        criterion: ParsedCriterion,
        scenario_type: str,
    ) -> List[str]:
        action = (
            criterion.action
            or "perform the requested action"
        )

        steps = [
            "Open the application.",
            "Navigate to the relevant page or module.",
        ]

        if scenario_type == "Positive":
            if criterion.condition:
                steps.append(
                    "Prepare inputs based on condition: "
                    f"{criterion.condition}."
                )

            steps.append(
                f"Perform the action: {action}."
            )

        elif scenario_type == "Negative":
            steps.append(
                "Enter invalid, incomplete, or restricted input data."
            )

            steps.append(
                f"Attempt to perform the action: {action}."
            )

        elif scenario_type == "Edge":
            steps.append(
                "Use blank, null, special-character, "
                "or unusual input combinations."
            )

            steps.append(
                f"Perform the action: {action}."
            )

        elif scenario_type == "Boundary":
            steps.append(
                "Prepare minimum, maximum, just-below-minimum, "
                "and just-above-maximum values."
            )

            steps.append(
                f"Perform the action: {action}."
            )

        elif scenario_type == "Security":
            steps.append(
                "Use an unauthorized, restricted, or "
                "insufficiently privileged user context."
            )

            steps.append(
                f"Attempt to perform the action: {action}."
            )

        return steps

    def build_preconditions(
        self,
        criterion: ParsedCriterion,
    ) -> List[str]:
        preconditions = [
            "User has access to the application."
        ]

        if criterion.actor:
            preconditions.append(
                f"{criterion.actor.capitalize()} is "
                "available in the test context."
            )

        if criterion.condition:
            preconditions.append(
                f"Condition available: {criterion.condition}."
            )

        return preconditions

    @staticmethod
    def resolve_priority(
        priority: str,
    ) -> str:
        """
        Ensures only supported priorities reach test generation.
        """

        valid_priorities = {
            "Low",
            "Medium",
            "High",
            "Critical",
        }

        if priority in valid_priorities:
            return priority

        return "Medium"

    @staticmethod
    def scenario_types_for_priority(
        priority: str,
    ) -> List[str]:
        """
        Determines test depth based on requirement priority.

        Low      -> 2 cases
        Medium   -> 3 cases
        High     -> 4 cases
        Critical -> 5 cases
        """

        mapping = {
            "Low": [
                "Positive",
                "Negative",
            ],
            "Medium": [
                "Positive",
                "Negative",
                "Edge",
            ],
            "High": [
                "Positive",
                "Negative",
                "Edge",
                "Boundary",
            ],
            "Critical": [
                "Positive",
                "Negative",
                "Edge",
                "Boundary",
                "Security",
            ],
        }

        return mapping.get(
            priority,
            mapping["Medium"],
        )

    @staticmethod
    def test_data_for_type(
        scenario_type: str,
    ) -> str:
        mapping = {
            "Positive": "Valid input data",
            "Negative": (
                "Invalid, blank, or incomplete input data"
            ),
            "Edge": (
                "Nulls, blanks, special characters, "
                "and unusual input combinations"
            ),
            "Boundary": (
                "Minimum, maximum, just-below, "
                "and just-above boundary values"
            ),
            "Security": (
                "Unauthorized user, restricted role, "
                "or invalid authorization context"
            ),
        }

        return mapping.get(
            scenario_type,
            "Applicable test data",
        )

    def generate_for_criterion(
        self,
        criterion: ParsedCriterion,
        index: int,
    ) -> List[TestCase]:
        test_cases: List[TestCase] = []

        priority = self.resolve_priority(
            criterion.priority
        )

        scenario_types = (
            self.scenario_types_for_priority(
                priority
            )
        )

        abbreviations = {
            "Positive": "P1",
            "Negative": "N1",
            "Edge": "E1",
            "Boundary": "B1",
            "Security": "S1",
        }

        for scenario_type in scenario_types:
            test_cases.append(
                TestCase(
                    test_case_id=(
                        f"TC-{index:03d}-"
                        f"{abbreviations[scenario_type]}"
                    ),
                    requirement_id=criterion.id,
                    scenario_type=scenario_type,
                    test_scenario=self.build_title(
                        criterion,
                        scenario_type,
                    ),
                    test_case_description=(
                        criterion.raw_text
                    ),
                    preconditions=self.build_preconditions(
                        criterion
                    ),
                    test_steps=self.build_steps(
                        criterion,
                        scenario_type,
                    ),
                    test_data=self.test_data_for_type(
                        scenario_type
                    ),
                    expected_result=(
                        self.expected_builder.build(
                            criterion,
                            scenario_type,
                        )
                    ),
                    priority=priority,
                    source_criterion=(
                        criterion.raw_text
                    ),
                )
            )

        return test_cases

    def generate(
        self,
        parsed_criteria: List[ParsedCriterion],
    ) -> List[TestCase]:
        all_test_cases: List[TestCase] = []

        for index, criterion in enumerate(
            parsed_criteria,
            start=1,
        ):
            generated_test_cases = (
                self.generate_for_criterion(
                    criterion,
                    index,
                )
            )

            all_test_cases.extend(
                generated_test_cases
            )

        return all_test_cases