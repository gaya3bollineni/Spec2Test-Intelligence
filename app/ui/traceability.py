from dataclasses import asdict
from typing import Any

import pandas as pd
import streamlit as st


def build_traceability_dataframe(
    traceability_rows: list[Any],
) -> pd.DataFrame:
    rows = []

    for row in traceability_rows:
        row_data = asdict(row)

        rows.append(
            {
                "Requirement ID": row_data["requirement_id"],
                "Acceptance Criteria": row_data["acceptance_criteria"],
                "Positive": row_data["positive_count"],
                "Negative": row_data["negative_count"],
                "Edge": row_data["edge_count"],
                "Total Test Cases": row_data["total_test_cases"],
                "Coverage": f'{row_data["coverage_percentage"]}%',
            }
        )

    return pd.DataFrame(rows)


def show_traceability_matrix(
    traceability_rows: list[Any],
) -> None:
    st.subheader("Requirement Traceability Matrix")

    if not traceability_rows:
        st.info("No traceability information is available.")
        return

    dataframe = build_traceability_dataframe(
        traceability_rows
    )

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )

    average_coverage = round(
        sum(
            row.coverage_percentage
            for row in traceability_rows
        )
        / len(traceability_rows)
    )

    st.caption(
        f"Overall requirement coverage: {average_coverage}%"
    )