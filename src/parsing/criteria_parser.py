import re
from typing import List, Optional

from src.models.schemas import (
    ParsedCriterion,
    RequirementItem,
)


class CriteriaParser:
    def __init__(self) -> None:
        self.rule_keywords = {
            "validation": [
                "error",
                "invalid",
                "blank",
                "required",
                "mandatory",
                "should not",
            ],
            "security": [
                "unauthorized",
                "forbidden",
                "access denied",
                "permission",
            ],
            "functional": [
                "should",
                "able to",
                "can",
                "must",
            ],
        }

    def detect_rule_type(
        self,
        text: str,
    ) -> str:
        lower_text = text.lower()

        for rule_type, keywords in self.rule_keywords.items():
            if any(
                keyword in lower_text
                for keyword in keywords
            ):
                return rule_type

        return "functional"

    def parse_given_when_then(
        self,
        text: str,
    ) -> Optional[dict[str, Optional[str]]]:
        """
        Parses Gherkin-style acceptance criteria:

        Given ...
        When ...
        Then ...
        """

        pattern = re.compile(
            r"given\s+(.*?)\s+when\s+(.*?)\s+then\s+(.*)",
            re.IGNORECASE,
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
            "expected_outcome": expected_outcome,
        }

    def parse_plain_text(
        self,
        text: str,
    ) -> dict[str, Optional[str]]:
        lower_text = text.lower()

        actor = None
        action = None
        condition = None
        expected_outcome = text.strip()

        actor_patterns = [
            "user",
            "admin",
            "customer",
            "system",
            "agent",
            "guest",
        ]

        for actor_pattern in actor_patterns:
            if re.search(
                rf"\b{actor_pattern}\b",
                lower_text,
            ):
                actor = actor_pattern
                break

        action_patterns = [
            "log in",
            "login",
            "register",
            "submit",
            "save",
            "update",
            "delete",
            "search",
            "upload",
            "download",
            "view",
            "reset password",
        ]

        for action_pattern in action_patterns:
            if action_pattern in lower_text:
                action = action_pattern
                break

        condition_patterns = [
            r"with valid .*",
            r"with invalid .*",
            r"when .*",
            r"if .*",
            r"using .*",
            r"for .*",
        ]

        for condition_pattern in condition_patterns:
            match = re.search(
                condition_pattern,
                lower_text,
            )

            if match:
                condition = match.group(0).strip()
                break

        return {
            "actor": actor,
            "action": action,
            "condition": condition,
            "expected_outcome": expected_outcome,
        }

    def parse_item(
        self,
        item: RequirementItem,
    ) -> ParsedCriterion:
        text = item.normalized_text

        parsed = self.parse_given_when_then(
            text
        )

        if not parsed:
            parsed = self.parse_plain_text(
                text
            )

        return ParsedCriterion(
            id=item.id,
            raw_text=item.raw_text,
            actor=parsed.get("actor"),
            action=parsed.get("action"),
            condition=parsed.get("condition"),
            expected_outcome=parsed.get(
                "expected_outcome"
            ),
            rule_type=self.detect_rule_type(
                text
            ),
            priority=item.priority,
        )

    def parse(
        self,
        items: List[RequirementItem],
    ) -> List[ParsedCriterion]:
        return [
            self.parse_item(item)
            for item in items
        ]