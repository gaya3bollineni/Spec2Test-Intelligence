from src.models.schemas import ParsedCriterion


class ExpectedResultBuilder:
    def build(self, criterion: ParsedCriterion, scenario_type: str = "Positive") -> str:
        text = (criterion.expected_outcome or criterion.raw_text).strip()

        if scenario_type == "Negative":
            if criterion.action in ["login", "log in"]:
                return "System should reject the login attempt and display an appropriate error message."
            if criterion.rule_type == "validation":
                return "System should display a validation error and should not proceed."
            return "System should prevent the action and display an appropriate error message."

        if scenario_type == "Edge":
            return "System should handle the boundary or edge input correctly without unexpected behavior."

        return text