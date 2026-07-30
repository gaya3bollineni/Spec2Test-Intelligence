import re
from typing import Any, List

from src.models.schemas import RequirementItem


class InputNormalizer:
    """
    Normalizes manual text input and structured requirement records.
    """

    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", "\n", text)

        return text.strip()

    def split_criteria(self, text: str) -> List[str]:
        """
        Splits manual text into separate acceptance criteria.

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

            is_list_item = (
                re.match(r"^\d+\.\s+", stripped)
                or re.match(r"^[-*•]\s+", stripped)
            )

            if is_list_item:
                if current:
                    criteria.append(current.strip())

                current = re.sub(
                    r"^\d+\.\s+|^[-*•]\s+",
                    "",
                    stripped,
                )
            else:
                if current:
                    current += f" {stripped}"
                else:
                    current = stripped

        if current:
            criteria.append(current.strip())

        if len(criteria) == 1:
            numbered_split = re.split(
                r"\s(?=\d+\.\s)",
                cleaned,
            )

            if len(numbered_split) > 1:
                criteria = [
                    re.sub(
                        r"^\d+\.\s+",
                        "",
                        item,
                    ).strip()
                    for item in numbered_split
                    if item.strip()
                ]

        return criteria

    def normalize(
        self,
        text: str,
    ) -> List[RequirementItem]:
        """
        Normalizes manually entered acceptance criteria.

        Requirement IDs are generated automatically and priority
        defaults to Medium.
        """

        items = self.split_criteria(text)
        normalized_items = []

        for index, item in enumerate(items, start=1):
            normalized_text = re.sub(
                r"\s+",
                " ",
                item.strip(),
            )

            normalized_items.append(
                RequirementItem(
                    id=f"AC-{index:03d}",
                    raw_text=item,
                    normalized_text=normalized_text,
                    priority="Medium",
                )
            )

        return normalized_items

    def normalize_records(
        self,
        records: List[dict[str, Any]],
    ) -> List[RequirementItem]:
        """
        Normalizes structured requirements imported from Excel.

        Expected record fields:
        - requirement_id
        - acceptance_criteria
        - priority
        """

        normalized_items = []

        for index, record in enumerate(records, start=1):
            raw_text = str(
                record.get(
                    "acceptance_criteria",
                    "",
                )
            ).strip()

            if not raw_text:
                continue

            requirement_id = str(
                record.get(
                    "requirement_id",
                    "",
                )
            ).strip()

            if not requirement_id:
                requirement_id = f"REQ-{index:03d}"

            priority = str(
                record.get(
                    "priority",
                    "Medium",
                )
            ).strip()

            if not priority:
                priority = "Medium"

            normalized_text = re.sub(
                r"\s+",
                " ",
                raw_text,
            )

            normalized_items.append(
                RequirementItem(
                    id=requirement_id,
                    raw_text=raw_text,
                    normalized_text=normalized_text,
                    priority=priority,
                )
            )

        return normalized_items