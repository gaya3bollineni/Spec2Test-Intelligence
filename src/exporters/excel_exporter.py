import pandas as pd
from typing import List
from src.models.schemas import TestCase


class ExcelExporter:
    def export(self, test_cases: List[TestCase], output_file: str = "generated_test_cases.xlsx") -> str:
        data = []

        for tc in test_cases:
            data.append({
                "Test Case ID": tc.test_case_id,
                "Requirement ID": tc.requirement_id,
                "Scenario Type": tc.scenario_type,
                "Test Scenario": tc.test_scenario,
                "Test Case Description": tc.test_case_description,
                "Preconditions": "\n".join(tc.preconditions),
                "Test Steps": "\n".join([f"{i + 1}. {step}" for i, step in enumerate(tc.test_steps)]),
                "Test Data": tc.test_data,
                "Expected Result": tc.expected_result,
                "Priority": tc.priority,
                "Source Criterion": tc.source_criterion,
            })

        df = pd.DataFrame(data)

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Generated Test Cases")

            worksheet = writer.sheets["Generated Test Cases"]

            for column_cells in worksheet.columns:
                max_length = 0
                column_letter = column_cells[0].column_letter

                for cell in column_cells:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))

                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)

            for row in worksheet.iter_rows():
                for cell in row:
                    cell.alignment = cell.alignment.copy(wrap_text=True, vertical="top")

        return output_file