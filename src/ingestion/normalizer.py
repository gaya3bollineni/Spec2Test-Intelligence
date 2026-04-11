import re
from typing import List
from src.models.schemas import RequirementItem


class InputNormalizer:
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        return text.strip()

    def split_criteria(self, text: str) -> List[str]:
        """
        Splits input text into separate acceptance criteria.
        Supports:
        - numbered lists: 1. 2. 3.
        - bullet points: -, *, •
        - plain line-by-line statements
        """
        cleaned = self.clean_text(text)

        if not cleaned:
            return []

        lines = cleaned.split("\n")
        criteria = []

        current = ""
        for line in lines:
            stripped = line.strip()

            if re.match(r"^\d+\.\s+", stripped) or re.match(r"^[-*•]\s+", stripped):
                if current:
                    criteria.append(current.strip())
                current = re.sub(r"^\d+\.\s+|^[-*•]\s+", "", stripped)
            else:
                if current:
                    current += " " + stripped
                else:
                    current = stripped

        if current:
            criteria.append(current.strip())

        # fallback if whole text is one paragraph with numbered sentences
        if len(criteria) == 1:
            numbered_split = re.split(r"\s(?=\d+\.\s)", cleaned)
            if len(numbered_split) > 1:
                criteria = [
                    re.sub(r"^\d+\.\s+", "", item).strip()
                    for item in numbered_split
                    if item.strip()
                ]

        return criteria

    def normalize(self, text: str) -> List[RequirementItem]:
        items = self.split_criteria(text)

        normalized_items = []
        for index, item in enumerate(items, start=1):
            normalized_text = item.strip()
            normalized_text = re.sub(r"\s+", " ", normalized_text)

            normalized_items.append(
                RequirementItem(
                    id=f"AC-{index:03d}",
                    raw_text=item,
                    normalized_text=normalized_text
                )
            )

        return normalized_items