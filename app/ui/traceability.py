from dataclasses import asdict
from typing import Any

import pandas as pd
import streamlit as st


def build_traceability_dataframe(
    traceability_rows: list[Any],
) -> pd.DataFrame:

    rows = []

    for row in traceability_rows:
        data = asdict(row)

        rows.append(
            {
                "Requirement ID": (
                    data["requirement_id"]
                ),
                "Acceptance Criteria": (
                    data["acceptance_criteria"]
                ),
                "Positive": (
                    data["positive_count"]
                ),
                "Negative": (
                    data["negative_count"]
                ),
                "Edge": (
                    data["edge_count"]
                ),
                "Boundary": (
                    data["boundary_count"]
                ),
                "Security": (
                    data["security_count"]
                ),
                "Generated": (
                    data["total_test_cases"]
                ),
                "Expected": (
                    data["expected_test_cases"]
                ),
                "Coverage": (
                    f'{data["coverage_percentage"]}%'
                ),
                "Status": (
                    data["coverage_status"]
                ),
            }
        )

    return pd.DataFrame(rows)


def show_traceability_matrix(
    traceability_rows: list[Any],
) -> None:

    st.subheader(
        "Requirement Traceability Matrix"
    )

    if not traceability_rows:
        st.info(
            "No traceability information is available."
        )
        return

    dataframe = build_traceability_dataframe(
        traceability_rows
    )

    st.dataframe(
        dataframe,
        width="stretch",
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
        f"Overall requirement coverage: "
        f"{average_coverage}%"
    )