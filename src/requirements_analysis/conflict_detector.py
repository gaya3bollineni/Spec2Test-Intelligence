import re
from dataclasses import dataclass
from typing import List

from src.models.schemas import ParsedCriterion


@dataclass
class ConflictingRequirement:
    requirement_id: str
    conflicts_with: str
    requirement_text: str
    conflicting_text: str
    reason: str


class ConflictRequirementDetector:
    """
    Detects simple direct contradictions between requirements.

    Example:
    - System should allow guest checkout.
    - System should not allow guest checkout.
    """

    NEGATIVE_MARKERS = {
        "should not",
        "must not",
        "cannot",
        "can't",
        "deny",
        "denied",
        "reject",
        "prevent",
        "block",
        "disallow",
    }

    POSITIVE_MARKERS = {
        "should",
        "must",
        "can",
        "allow",
        "allowed",
        "enable",
        "permit",
    }

    def detect(
        self,
        parsed_items: List[ParsedCriterion],
    ) -> List[ConflictingRequirement]:
        conflicts: List[ConflictingRequirement] = []

        for index, first in enumerate(parsed_items):
            for second in parsed_items[index + 1:]:
                if self._requirements_conflict(
                    first.raw_text,
                    second.raw_text,
                ):
                    conflicts.append(
                        ConflictingRequirement(
                            requirement_id=second.id,
                            conflicts_with=first.id,
                            requirement_text=second.raw_text,
                            conflicting_text=first.raw_text,
                            reason=(
                                "The requirements appear to describe "
                                "opposite behavior for the same action."
                            ),
                        )
                    )

        return conflicts

    def _requirements_conflict(
        self,
        first_text: str,
        second_text: str,
    ) -> bool:
        first_normalized = self._normalize(first_text)
        second_normalized = self._normalize(second_text)

        first_is_negative = self._is_negative(
            first_normalized
        )
        second_is_negative = self._is_negative(
            second_normalized
        )

        if first_is_negative == second_is_negative:
            return False

        first_core = self._remove_polarity_words(
            first_normalized
        )
        second_core = self._remove_polarity_words(
            second_normalized
        )

        return first_core == second_core

    def _is_negative(
        self,
        text: str,
    ) -> bool:
        return any(
            marker in text
            for marker in self.NEGATIVE_MARKERS
        )

    def _remove_polarity_words(
        self,
        text: str,
    ) -> str:
        cleaned = text

        markers = (
            self.NEGATIVE_MARKERS
            | self.POSITIVE_MARKERS
        )

        for marker in sorted(
            markers,
            key=len,
            reverse=True,
        ):
            cleaned = cleaned.replace(
                marker,
                ""
            )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        )

        return cleaned.strip()

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        text = text.lower().strip()

        text = re.sub(
            r"[^\w\s]",
            "",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text