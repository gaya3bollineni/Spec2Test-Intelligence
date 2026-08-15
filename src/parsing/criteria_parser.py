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
        Parses strict Gherkin-style acceptance criteria:

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

        actor = self._detect_actor(
            f"{condition} {action} {expected_outcome}"
        )

        return {
            "actor": actor or "user",
            "action": action,
            "condition": condition,
            "expected_outcome": expected_outcome,
        }

    def parse_loose_gherkin(
        self,
        text: str,
    ) -> Optional[dict[str, Optional[str]]]:
        """
        Parses conversational or incomplete Gherkin-like criteria.

        Example:

        Given user is on login
        and user enter valid credentials and password
        they verify user is logged in
        and can see home page
        """

        normalized_text = " ".join(
            text.split()
        )

        lower_text = normalized_text.lower()

        if not lower_text.startswith("given "):
            return None

        condition = None
        action = None
        expected_outcome = None

        # Capture the initial Given condition.
        condition_match = re.match(
            r"given\s+(.*?)(?=\s+and\s+|\s+when\s+|\s+then\s+|\s+verify\s+|\s+they\s+verify\s+|$)",
            normalized_text,
            re.IGNORECASE,
        )

        if condition_match:
            condition = condition_match.group(1).strip()

        # Look for an action after "and", "when", etc.
        action_patterns = [
            r"(?:and|when)\s+(user|customer|admin|agent|guest|system)?\s*(.*?)(?=\s+then\s+|\s+verify\s+|\s+they\s+verify\s+|\s+and\s+can\s+|\s+and\s+should\s+|$)",
            r"(?:and|when)\s+(.*?)(?=\s+then\s+|\s+verify\s+|\s+they\s+verify\s+|$)",
        ]

        for pattern in action_patterns:
            action_match = re.search(
                pattern,
                normalized_text,
                re.IGNORECASE,
            )

            if action_match:
                if action_match.lastindex == 2:
                    possible_action = action_match.group(2)
                else:
                    possible_action = action_match.group(1)

                if possible_action:
                    action = possible_action.strip()
                    break

        # Detect result language such as:
        # "then ...", "verify ...", "they verify ...", "and can see ..."
        result_patterns = [
            r"\bthen\s+(.*)",
            r"\bthey\s+verify\s+(.*)",
            r"\bverify\s+(.*)",
        ]

        for pattern in result_patterns:
            result_match = re.search(
                pattern,
                normalized_text,
                re.IGNORECASE,
            )

            if result_match:
                expected_outcome = (
                    result_match.group(1).strip()
                )
                break

        # If the result continues with "and can ..."
        if expected_outcome:
            continuation_match = re.search(
                r"(?:they\s+verify|verify)\s+.*?\s+(and\s+can\s+.*)$",
                normalized_text,
                re.IGNORECASE,
            )

            if continuation_match:
                continuation = (
                    continuation_match.group(1).strip()
                )

                if continuation.lower() not in expected_outcome.lower():
                    expected_outcome = (
                        f"{expected_outcome} {continuation}"
                    )

        # Fallback: if action wasn't captured cleanly,
        # detect common action phrases from the whole text.
        if not action:
            action = self._detect_action(
                normalized_text
            )

        actor = self._detect_actor(
            normalized_text
        )

        if not condition and not action and not expected_outcome:
            return None

        return {
            "actor": actor or "user",
            "action": action,
            "condition": condition,
            "expected_outcome": expected_outcome,
        }

    def parse_plain_text(
        self,
        text: str,
    ) -> dict[str, Optional[str]]:
        lower_text = text.lower()

        actor = self._detect_actor(
            lower_text
        )

        action = self._detect_action(
            lower_text
        )

        condition = None
        expected_outcome = text.strip()

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

    @staticmethod
    def _detect_actor(
        text: str,
    ) -> Optional[str]:
        lower_text = text.lower()

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
                return actor_pattern

        return None

    @staticmethod
    def _detect_action(
        text: str,
    ) -> Optional[str]:
        lower_text = text.lower()

        action_patterns = [
            "reset password",
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
            "enter valid credentials",
            "enter valid credentials and password",
            "enter credentials",
        ]

        for action_pattern in action_patterns:
            if action_pattern in lower_text:
                return action_pattern

        return None

    def parse_item(
        self,
        item: RequirementItem,
    ) -> ParsedCriterion:
        text = item.normalized_text

        parsed = self.parse_given_when_then(
            text
        )

        if not parsed:
            parsed = self.parse_loose_gherkin(
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