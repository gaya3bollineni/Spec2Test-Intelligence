import re
from typing import List
from src.models.schemas import RequirementItem, ParsedCriterion


class CriteriaParser:
    def __init__(self):
        self.rule_keywords = {
            "validation": ["error", "invalid", "blank", "required", "mandatory", "should not"],
            "security": ["unauthorized", "forbidden", "access denied", "permission"],
            "functional": ["should", "able to", "can", "must"]
        }

    def detect_rule_type(self, text: str) -> str:
        lower_text = text.lower()

        for rule_type, keywords in self.rule_keywords.items():
            if any(keyword in lower_text for keyword in keywords):
                return rule_type

        return "functional"

    def parse_given_when_then(self, text: str):
        """
        Parses Gherkin-style acceptance criteria:
        Given ...
        When ...
        Then ...
        """
        pattern = re.compile(
            r"given\s+(.*?)\s+when\s+(.*?)\s+then\s+(.*)",
            re.IGNORECASE
        )
        match = pattern.search(text)

        if not match:
            return None

        condition = match.group(1).strip()
        action = match.group(2).strip()
        expected_outcome = match.group(3).strip()

        return {
            "actor": "user",
            "action": action,
            "condition": condition,
            "expected_outcome": expected_outcome
        }

    def parse_plain_text(self, text: str):
        lower_text = text.lower()

        actor = None
        action = None
        condition = None
        expected_outcome = text.strip()

        actor_patterns = [
            r"user",
            r"admin",
            r"customer",
            r"system",
            r"agent",
            r"guest"
        ]

        for pattern in actor_patterns:
            if re.search(rf"\b{pattern}\b", lower_text):
                actor = pattern
                break

        action_patterns = [
            r"log in",
            r"login",
            r"register",
            r"submit",
            r"save",
            r"update",
            r"delete",
            r"search",
            r"upload",
            r"download",
            r"view",
            r"reset password"
        ]

        for pattern in action_patterns:
            if pattern in lower_text:
                action = pattern
                break

        condition_patterns = [
            r"with valid .*",
            r"with invalid .*",
            r"when .*",
            r"if .*",
            r"using .*",
            r"for .*"
        ]

        for pattern in condition_patterns:
            match = re.search(pattern, lower_text)
            if match:
                condition = match.group(0).strip()
                break

        return {
            "actor": actor,
            "action": action,
            "condition": condition,
            "expected_outcome": expected_outcome
        }

    def parse_item(self, item: RequirementItem) -> ParsedCriterion:
        text = item.normalized_text

        parsed = self.parse_given_when_then(text)

        if not parsed:
            parsed = self.parse_plain_text(text)

        return ParsedCriterion(
            id=item.id,
            raw_text=item.raw_text,
            actor=parsed.get("actor"),
            action=parsed.get("action"),
            condition=parsed.get("condition"),
            expected_outcome=parsed.get("expected_outcome"),
            rule_type=self.detect_rule_type(text)
        )

    def parse(self, items: List[RequirementItem]) -> List[ParsedCriterion]:
        return [self.parse_item(item) for item in items]