from io import BytesIO
from typing import Any, BinaryIO

import pandas as pd


class ExcelRequirementLoader:
    """Loads structured requirements from an Excel workbook."""

    COLUMN_ALIASES = {
        "acceptance criteria": "acceptance_criteria",
        "acceptance criterion": "acceptance_criteria",
        "acceptance_criteria": "acceptance_criteria",
        "criteria": "acceptance_criteria",
        "requirement": "acceptance_criteria",
        "requirements": "acceptance_criteria",
        "requirement id": "requirement_id",
        "requirement_id": "requirement_id",
        "id": "requirement_id",
        "priority": "priority",
        "severity": "priority",
    }

    def load(
        self,
        uploaded_file: BinaryIO | BytesIO,
    ) -> pd.DataFrame:
        try:
            dataframe = pd.read_excel(
                uploaded_file,
                sheet_name=0,
            )
        except Exception as error:
            raise ValueError(
                "Unable to read the Excel file. "
                "Please upload a valid .xlsx workbook."
            ) from error

        if dataframe.empty:
            raise ValueError(
                "The uploaded Excel file does not contain any rows."
            )

        dataframe = self._normalize_columns(
            dataframe
        )

        if "acceptance_criteria" not in dataframe.columns:
            raise ValueError(
                "The Excel file must contain an "
                "Acceptance Criteria column."
            )

        dataframe = dataframe.dropna(
            subset=["acceptance_criteria"]
        ).copy()

        dataframe["acceptance_criteria"] = (
            dataframe["acceptance_criteria"]
            .astype(str)
            .str.strip()
        )

        dataframe = dataframe[
            dataframe["acceptance_criteria"] != ""
        ].reset_index(drop=True)

        if dataframe.empty:
            raise ValueError(
                "No valid acceptance criteria were found "
                "in the uploaded file."
            )

        dataframe = self._prepare_requirement_ids(
            dataframe
        )

        dataframe = self._prepare_priorities(
            dataframe
        )

        return dataframe

    def to_records(
        self,
        dataframe: pd.DataFrame,
    ) -> list[dict[str, Any]]:
        """
        Converts the Excel DataFrame into structured records
        for the requirement-processing pipeline.
        """

        required_columns = {
            "requirement_id",
            "acceptance_criteria",
            "priority",
        }

        missing_columns = required_columns.difference(
            dataframe.columns
        )

        if missing_columns:
            raise ValueError(
                "The requirement data is missing required "
                f"columns: {', '.join(sorted(missing_columns))}."
            )

        return dataframe[
            [
                "requirement_id",
                "acceptance_criteria",
                "priority",
            ]
        ].to_dict(
            orient="records"
        )

    def to_text(
        self,
        dataframe: pd.DataFrame,
    ) -> str:
        """
        Retained for compatibility with the manual text workflow.
        """

        return "\n".join(
            dataframe["acceptance_criteria"].tolist()
        )

    def _normalize_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        dataframe = dataframe.copy()
        renamed_columns = {}

        for column in dataframe.columns:
            normalized_column = (
                str(column)
                .strip()
                .lower()
            )

            renamed_columns[column] = (
                self.COLUMN_ALIASES.get(
                    normalized_column,
                    normalized_column.replace(
                        " ",
                        "_",
                    ),
                )
            )

        return dataframe.rename(
            columns=renamed_columns
        )

    def _prepare_requirement_ids(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        dataframe = dataframe.copy()

        if "requirement_id" not in dataframe.columns:
            dataframe["requirement_id"] = [
                f"REQ-{index:03d}"
                for index in range(
                    1,
                    len(dataframe) + 1,
                )
            ]

            return dataframe

        requirement_ids = (
            dataframe["requirement_id"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        dataframe["requirement_id"] = [
            requirement_id
            if requirement_id
            else f"REQ-{index:03d}"
            for index, requirement_id in enumerate(
                requirement_ids,
                start=1,
            )
        ]

        return dataframe

    def _prepare_priorities(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        dataframe = dataframe.copy()

        if "priority" not in dataframe.columns:
            dataframe["priority"] = "Medium"

            return dataframe

        priorities = (
            dataframe["priority"]
            .fillna("Medium")
            .astype(str)
            .str.strip()
        )

        valid_priorities = {
            "low": "Low",
            "medium": "Medium",
            "high": "High",
            "critical": "Critical",
        }

        dataframe["priority"] = [
            valid_priorities.get(
                priority.lower(),
                "Medium",
            )
            for priority in priorities
        ]

        return dataframe