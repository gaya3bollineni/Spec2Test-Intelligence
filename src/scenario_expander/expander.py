from typing import List

from src.models.schemas import (
    ParsedCriterion,
    TestCase,
)
from src.oracle_builder.expected_result_builder import (
    ExpectedResultBuilder,
)


class ScenarioExpander:
    def __init__(self) -> None:
        self.expected_builder = (
            ExpectedResultBuilder()
        )

    def build_title(
        self,
        criterion: ParsedCriterion,
        scenario_type: str,
    ) -> str:
        action = (
            criterion.action
            if criterion.action
            else "perform action"
        )

        actor = (
            criterion.actor
            if criterion.actor
            else "user"
        )

        if scenario_type == "Positive":
            return (
                f"Validate {actor} can "
                f"{action} successfully"
            )

        if scenario_type == "Negative":
            return (
                f"Validate {actor} cannot "
                f"{action} with invalid input"
            )

        if scenario_type == "Edge":
            return (
                "Validate boundary and edge "
                f"behavior for {action}"
            )

        return f"Validate {action}"

    def build_steps(
        self,
        criterion: ParsedCriterion,
        scenario_type: str,
    ) -> List[str]:
        action = (
            criterion.action
            if criterion.action
            else "perform the requested action"
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

            return steps

        if scenario_type == "Negative":
            steps.append(
                "Enter invalid, incomplete, or "
                "restricted input data."
            )

            steps.append(
                f"Attempt to perform the action: {action}."
            )

            return steps

        if scenario_type == "Edge":
            steps.append(
                "Enter boundary, null, blank, special "
                "character, or maximum/minimum values."
            )

            steps.append(
                f"Perform the action: {action}."
            )

            return steps

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

        if (
            criterion.condition
            and "given"
            not in criterion.condition.lower()
        ):
            preconditions.append(
                "Condition available: "
                f"{criterion.condition}."
            )

        return preconditions

    @staticmethod
    def resolve_priority(
        criterion: ParsedCriterion,
    ) -> str:
        valid_priorities = {
            "Low",
            "Medium",
            "High",
            "Critical",
        }

        if criterion.priority in valid_priorities:
            return criterion.priority

        return "Medium"

    def generate_for_criterion(
        self,
        criterion: ParsedCriterion,
        index: int,
    ) -> List[TestCase]:
        test_cases: List[TestCase] = []

        priority = self.resolve_priority(
            criterion
        )

        test_cases.append(
            TestCase(
                test_case_id=f"TC-{index:03d}-P1",
                requirement_id=criterion.id,
                scenario_type="Positive",
                test_scenario=self.build_title(
                    criterion,
                    "Positive",
                ),
                test_case_description=(
                    criterion.raw_text
                ),
                preconditions=self.build_preconditions(
                    criterion
                ),
                test_steps=self.build_steps(
                    criterion,
                    "Positive",
                ),
                test_data="Valid input data",
                expected_result=(
                    self.expected_builder.build(
                        criterion,
                        "Positive",
                    )
                ),
                priority=priority,
                source_criterion=criterion.raw_text,
            )
        )

        test_cases.append(
            TestCase(
                test_case_id=f"TC-{index:03d}-N1",
                requirement_id=criterion.id,
                scenario_type="Negative",
                test_scenario=self.build_title(
                    criterion,
                    "Negative",
                ),
                test_case_description=(
                    "System should not allow invalid "
                    "input and should display an "
                    "appropriate error message."
                ),
                preconditions=self.build_preconditions(
                    criterion
                ),
                test_steps=self.build_steps(
                    criterion,
                    "Negative",
                ),
                test_data=(
                    "Invalid, blank, or incomplete "
                    "input data"
                ),
                expected_result=(
                    self.expected_builder.build(
                        criterion,
                        "Negative",
                    )
                ),
                priority=priority,
                source_criterion=criterion.raw_text,
            )
        )

        test_cases.append(
            TestCase(
                test_case_id=f"TC-{index:03d}-E1",
                requirement_id=criterion.id,
                scenario_type="Edge",
                test_scenario=self.build_title(
                    criterion,
                    "Edge",
                ),
                test_case_description=(
                    "System should handle boundary "
                    "and edge-case inputs correctly."
                ),
                preconditions=self.build_preconditions(
                    criterion
                ),
                test_steps=self.build_steps(
                    criterion,
                    "Edge",
                ),
                test_data=(
                    "Boundary values, nulls, blanks, "
                    "special characters, and "
                    "minimum/maximum values"
                ),
                expected_result=(
                    self.expected_builder.build(
                        criterion,
                        "Edge",
                    )
                ),
                priority=priority,
                source_criterion=criterion.raw_text,
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