import re
from typing import Optional

from pydantic import BaseModel

from src.playwright.dom_models import (
    DOMElement,
)


class ElementMatch(BaseModel):
    element: DOMElement
    score: int
    matched_by: list[str]


class DOMElementMatcher:
    """
    Deterministically matches an automation target
    such as "Email", "Country", or "Sign In" against
    elements extracted from the uploaded DOM.
    """

    def match(
        self,
        target: str,
        elements: list[DOMElement],
        expected_tag: Optional[str] = None,
        expected_type: Optional[str] = None,
    ) -> Optional[ElementMatch]:
        if not target or not target.strip():
            return None

        target_normalized = self._normalize(
            target
        )

        if not target_normalized:
            return None

        candidates: list[
            ElementMatch
        ] = []

        for element in elements:
            score = 0
            matched_by: list[str] = []

            fields = [
                (
                    "label",
                    element.label,
                    100,
                ),
                (
                    "aria_label",
                    element.aria_label,
                    95,
                ),
                (
                    "text",
                    element.text,
                    90,
                ),
                (
                    "name",
                    element.name,
                    80,
                ),
                (
                    "placeholder",
                    element.placeholder,
                    75,
                ),
                (
                    "id",
                    element.element_id,
                    65,
                ),
                (
                    "test_id",
                    element.test_id,
                    60,
                ),
            ]

            for (
                field_name,
                field_value,
                weight,
            ) in fields:
                field_score = (
                    self._score_value(
                        target_normalized,
                        field_value,
                        weight,
                    )
                )

                if field_score:
                    score += field_score

                    matched_by.append(
                        field_name
                    )

            if (
                expected_tag
                and element.tag
                == expected_tag.lower()
            ):
                score += 20

                matched_by.append(
                    "tag"
                )

            if (
                expected_type
                and element.element_type
                and element.element_type.lower()
                == expected_type.lower()
            ):
                score += 20

                matched_by.append(
                    "type"
                )

            if score > 0:
                candidates.append(
                    ElementMatch(
                        element=element,
                        score=score,
                        matched_by=matched_by,
                    )
                )

        if not candidates:
            return None

        candidates.sort(
            key=lambda candidate: (
                candidate.score,
                self._stability_score(
                    candidate.element
                ),
            ),
            reverse=True,
        )

        return candidates[0]

    def _score_value(
        self,
        target: str,
        value: Optional[str],
        weight: int,
    ) -> int:
        if not value:
            return 0

        normalized_value = (
            self._normalize(value)
        )

        if not normalized_value:
            return 0

        if target == normalized_value:
            return weight

        target_tokens = set(
            target.split()
        )

        value_tokens = set(
            normalized_value.split()
        )

        if not target_tokens:
            return 0

        overlap = (
            target_tokens
            & value_tokens
        )

        if not overlap:
            return 0

        overlap_ratio = (
            len(overlap)
            / len(target_tokens)
        )

        if overlap_ratio == 1:
            return int(
                weight * 0.8
            )

        if overlap_ratio >= 0.5:
            return int(
                weight * 0.5
            )

        return 0

    @staticmethod
    def _stability_score(
        element: DOMElement,
    ) -> int:
        score = 0

        if element.label:
            score += 5

        if element.aria_label:
            score += 4

        if element.test_id:
            score += 3

        if element.element_id:
            score += 2

        if element.placeholder:
            score += 1

        return score

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:
        value = re.sub(
            r"([a-z])([A-Z])",
            r"\1 \2",
            value,
        )

        value = value.replace(
            "_",
            " ",
        )

        value = value.replace(
            "-",
            " ",
        )

        value = re.sub(
            r"[^a-zA-Z0-9\s]",
            " ",
            value,
        )

        return " ".join(
            value.lower().split()
        )