import pandas as pd
import streamlit as st

from src.data_testing.generator import (
    DataTestGenerator,
)
from src.data_testing.models import (
    DataFieldRule,
)


def show_data_testing() -> None:

    st.subheader(
        "Data Testing"
    )

    st.caption(
        "Define data rules and generate validation scenarios."
    )

    uploaded_file = st.file_uploader(
        "Upload Data Rule Excel",
        type=["xlsx"],
        key="data_rule_excel",
    )

    if uploaded_file is None:
        st.info(
            "Upload a data rule workbook to generate "
            "data validation scenarios."
        )
        return

    dataframe = pd.read_excel(
        uploaded_file
    )

    st.dataframe(
        dataframe,
        width="stretch",
        hide_index=True,
    )

    required_columns = {
        "Field Name",
        "Data Type",
    }

    if not required_columns.issubset(
        dataframe.columns
    ):
        st.error(
            "The workbook must contain "
            "'Field Name' and 'Data Type' columns."
        )
        return

    if not st.button(
        "Generate Data Test Scenarios",
        type="primary",
    ):
        return

    rules = []

    for _, row in dataframe.iterrows():

        allowed_values = None

        if pd.notna(
            row.get(
                "Allowed Values"
            )
        ):
            allowed_values = [
                value.strip()
                for value in str(
                    row["Allowed Values"]
                ).split(",")
                if value.strip()
            ]

        rules.append(
            DataFieldRule(
                field_name=str(
                    row["Field Name"]
                ),
                data_type=str(
                    row["Data Type"]
                ),
                required=str(
                    row.get(
                        "Required",
                        "No",
                    )
                ).lower()
                in {
                    "yes",
                    "true",
                    "1",
                },
                minimum=(
                    float(row["Min"])
                    if pd.notna(
                        row.get("Min")
                    )
                    else None
                ),
                maximum=(
                    float(row["Max"])
                    if pd.notna(
                        row.get("Max")
                    )
                    else None
                ),
                allowed_values=allowed_values,
                unique=str(
                    row.get(
                        "Unique",
                        "No",
                    )
                ).lower()
                in {
                    "yes",
                    "true",
                    "1",
                },
            )
        )

    generator = DataTestGenerator()

    scenarios = generator.generate(
        rules
    )

    result_dataframe = pd.DataFrame(
        [
            {
                "Test ID": scenario.test_id,
                "Field": scenario.field_name,
                "Type": scenario.test_type,
                "Description": scenario.description,
                "Expected Result": (
                    scenario.expected_result
                ),
            }
            for scenario in scenarios
        ]
    )

    st.success(
        f"Generated {len(scenarios)} "
        "data validation scenarios."
    )

    st.dataframe(
        result_dataframe,
        width="stretch",
        hide_index=True,
    )