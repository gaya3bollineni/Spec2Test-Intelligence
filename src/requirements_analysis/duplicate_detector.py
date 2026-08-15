import re
from dataclasses import dataclass
from typing import List

from src.models.schemas import ParsedCriterion


@dataclass
class DuplicateRequirement:
    requirement_id: str
    duplicate_of: str
    requirement_text: str
    duplicate_text: str


class DuplicateRequirementDetector:
    """
    Detects duplicate requirements after normalizing
    capitalization, whitespace, and punctuation.
    """

    def detect(
        self,
        parsed_items: List[ParsedCriterion],
    ) -> List[DuplicateRequirement]:

        duplicates: List[DuplicateRequirement] = []
        seen_requirements: dict[str, ParsedCriterion] = {}

        for item in parsed_items:
            normalized_text = self._normalize_text(
                item.raw_text
            )

            if normalized_text in seen_requirements:
                original = seen_requirements[
                    normalized_text
                ]

                duplicates.append(
                    DuplicateRequirement(
                        requirement_id=item.id,
                        duplicate_of=original.id,
                        requirement_text=item.raw_text,
                        duplicate_text=original.raw_text,
                    )
                )
            else:
                seen_requirements[
                    normalized_text
                ] = item

        return duplicates

    @staticmethod
    def _normalize_text(
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