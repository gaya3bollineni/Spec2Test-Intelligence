from typing import List
from src.models.schemas import ParsedCriterion, TestCase
from src.oracle_builder.expected_result_builder import ExpectedResultBuilder


class ScenarioExpander:
    def __init__(self):
        self.expected_builder = ExpectedResultBuilder()

    def build_title(self, criterion: ParsedCriterion, scenario_type: str) -> str:
        action = criterion.action if criterion.action else "perform action"
        actor = criterion.actor if criterion.actor else "user"

        if scenario_type == "Positive":
            return f"Validate {actor} can {action} successfully"

        if scenario_type == "Negative":
            return f"Validate {actor} cannot {action} with invalid input"

        if scenario_type == "Edge":
            return f"Validate boundary and edge behavior for {action}"

        return f"Validate {action}"

    def build_steps(self, criterion: ParsedCriterion, scenario_type: str) -> List[str]:
        action = criterion.action if criterion.action else "perform the requested action"

        steps = ["Open the application."]

        if scenario_type == "Positive":
            steps.append("Navigate to the relevant page or module.")
            if criterion.condition:
                steps.append(f"Prepare inputs based on condition: {criterion.condition}.")
            steps.append(f"Perform the action: {action}.")
            return steps

        if scenario_type == "Negative":
            steps.append("Navigate to the relevant page or module.")
            steps.append("Enter invalid, incomplete, or restricted input data.")
            steps.append(f"Attempt to perform the action: {action}.")
            return steps

        if scenario_type == "Edge":
            steps.append("Navigate to the relevant page or module.")
            steps.append("Enter boundary, null, blank, special character, or max/min input values.")
            steps.append(f"Perform the action: {action}.")
            return steps

        return steps

    def build_preconditions(self, criterion: ParsedCriterion) -> List[str]:
        preconditions = ["User has access to the application."]
        if criterion.actor:
            preconditions.append(f"{criterion.actor.capitalize()} is available in the test context.")
        if criterion.condition and "given" not in criterion.condition.lower():
            preconditions.append(f"Condition available: {criterion.condition}.")
        return preconditions

    def generate_for_criterion(self, criterion: ParsedCriterion, index: int) -> List[TestCase]:
        test_cases: List[TestCase] = []

        # Positive
        positive_id = f"TC-{index:03d}-P1"
        test_cases.append(
            TestCase(
                test_case_id=positive_id,
                title=self.build_title(criterion, "Positive"),
                scenario=criterion.raw_text,
                preconditions=self.build_preconditions(criterion),
                test_steps=self.build_steps(criterion, "Positive"),
                expected_result=self.expected_builder.build(criterion, "Positive"),
                priority="High" if criterion.rule_type in ["functional", "validation"] else "Medium",
                test_type="Positive",
                source_criterion_id=criterion.id,
            )
        )

        # Negative
        negative_id = f"TC-{index:03d}-N1"
        test_cases.append(
            TestCase(
                test_case_id=negative_id,
                title=self.build_title(criterion, "Negative"),
                scenario=f"Negative validation for: {criterion.raw_text}",
                preconditions=self.build_preconditions(criterion),
                test_steps=self.build_steps(criterion, "Negative"),
                expected_result=self.expected_builder.build(criterion, "Negative"),
                priority="High",
                test_type="Negative",
                source_criterion_id=criterion.id,
            )
        )

        # Edge
        edge_id = f"TC-{index:03d}-E1"
        test_cases.append(
            TestCase(
                test_case_id=edge_id,
                title=self.build_title(criterion, "Edge"),
                scenario=f"Edge and boundary validation for: {criterion.raw_text}",
                preconditions=self.build_preconditions(criterion),
                test_steps=self.build_steps(criterion, "Edge"),
                expected_result=self.expected_builder.build(criterion, "Edge"),
                priority="Medium",
                test_type="Edge",
                source_criterion_id=criterion.id,
            )
        )

        return test_cases

    def generate(self, parsed_criteria: List[ParsedCriterion]) -> List[TestCase]:
        all_test_cases: List[TestCase] = []

        for index, criterion in enumerate(parsed_criteria, start=1):
            generated = self.generate_for_criterion(criterion, index)
            all_test_cases.extend(generated)

        return all_test_cases