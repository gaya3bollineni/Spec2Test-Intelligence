from io import BytesIO

import pandas as pd


def build_requirements_template() -> bytes:
    """
    Creates a sample Excel requirements template.
    """

    template_dataframe = pd.DataFrame(
        {
            "Requirement ID": [
                "REQ-001",
                "REQ-002",
                "REQ-003",
            ],
            "Acceptance Criteria": [
                "User should be able to log in with valid credentials.",
                "The system should display an error for invalid credentials.",
                "The account should lock after five failed login attempts.",
            ],
            "Priority": [
                "High",
                "High",
                "Medium",
            ],
        }
    )

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        template_dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Requirements",
        )

    output.seek(0)

    return output.getvalue()