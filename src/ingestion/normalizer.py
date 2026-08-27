import re
from typing import Any, List

from src.models.schemas import RequirementItem


class InputNormalizer:
    """
    Normalizes manual text input and structured requirement records.
    """

    def clean_text(
        self,
        text: str,
    ) -> str:
        if not text:
            return ""

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        # Preserve line structure because multiline
        # Given/When/Then blocks depend on it.
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    def split_criteria(
        self,
        text: str,
    ) -> List[str]:
        """
        Splits manual input into separate acceptance criteria.

        Supports:
        - numbered lists
        - bullet lists
        - multiple Given/When/Then blocks
        - existing single multiline Gherkin criteria
        - legacy plain-text input
        """

        cleaned = self.clean_text(
            text
        )

        if not cleaned:
            return []

        # -----------------------------------------------------
        # 1. MULTIPLE GHERKIN BLOCKS
        # -----------------------------------------------------
        #
        # Example:
        #
        # Given ...
        # When ...
        # Then ...
        #
        # Given ...
        # When ...
        # Then ...
        #
        # Each new line beginning with Given starts
        # a new requirement.
        # -----------------------------------------------------

        gherkin_blocks = (
            self._split_gherkin_blocks(
                cleaned
            )
        )

        if len(gherkin_blocks) > 1:
            return gherkin_blocks

        # -----------------------------------------------------
        # 2. NUMBERED / BULLETED REQUIREMENTS
        # -----------------------------------------------------

        lines = cleaned.split(
            "\n"
        )

        criteria: List[str] = []

        current = ""

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            is_list_item = bool(
                re.match(
                    r"^\d+\.\s+",
                    stripped,
                )
                or re.match(
                    r"^[-*•]\s+",
                    stripped,
                )
            )

            if is_list_item:
                if current:
                    criteria.append(
                        current.strip()
                    )

                current = re.sub(
                    r"^\d+\.\s+|^[-*•]\s+",
                    "",
                    stripped,
                )

            else:
                if current:
                    current += (
                        f" {stripped}"
                    )
                else:
                    current = stripped

        if current:
            criteria.append(
                current.strip()
            )

        # -----------------------------------------------------
        # 3. INLINE NUMBERED LIST FALLBACK
        # -----------------------------------------------------

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

    def _split_gherkin_blocks(
        self,
        text: str,
    ) -> List[str]:
        """
        Splits multiple multiline Gherkin blocks.

        A new line beginning with "Given" starts
        a new requirement.

        A single Given/When/Then block remains one
        requirement.
        """

        lines = text.split(
            "\n"
        )

        blocks: List[str] = []
        current_lines: List[str] = []

        given_count = 0

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            starts_given = bool(
                re.match(
                    r"^given\b",
                    stripped,
                    re.IGNORECASE,
                )
            )

            if starts_given:
                given_count += 1

                if current_lines:
                    blocks.append(
                        " ".join(
                            current_lines
                        ).strip()
                    )

                    current_lines = []

            current_lines.append(
                stripped
            )

        if current_lines:
            blocks.append(
                " ".join(
                    current_lines
                ).strip()
            )

        # Only use Gherkin-block splitting when
        # multiple Given clauses were actually found.
        if given_count > 1:
            return [
                block
                for block in blocks
                if block
            ]

        return [
            text.strip()
        ]

    def normalize(
        self,
        text: str,
    ) -> List[RequirementItem]:
        """
        Normalizes manually entered acceptance criteria.

        Requirement IDs are generated automatically.
        Priority defaults to Medium.
        """

        items = self.split_criteria(
            text
        )

        normalized_items: List[
            RequirementItem
        ] = []

        for index, item in enumerate(
            items,
            start=1,
        ):
            normalized_text = re.sub(
                r"\s+",
                " ",
                item.strip(),
            )

            normalized_items.append(
                RequirementItem(
                    id=(
                        f"AC-{index:03d}"
                    ),
                    raw_text=item,
                    normalized_text=(
                        normalized_text
                    ),
                    priority="Medium",
                )
            )

        return normalized_items

    def normalize_records(
        self,
        records: List[
            dict[str, Any]
        ],
    ) -> List[RequirementItem]:
        """
        Normalizes structured requirements imported
        from Excel.

        Expected fields:
        - requirement_id
        - acceptance_criteria
        - priority
        """

        normalized_items: List[
            RequirementItem
        ] = []

        for index, record in enumerate(
            records,
            start=1,
        ):
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
                requirement_id = (
                    f"REQ-{index:03d}"
                )

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
                    normalized_text=(
                        normalized_text
                    ),
                    priority=priority,
                )
            )

        return normalized_items