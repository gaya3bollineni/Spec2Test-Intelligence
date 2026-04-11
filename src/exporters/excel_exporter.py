import pandas as pd
from typing import List
from src.models.schemas import TestCase


class ExcelExporter:
    def export(self, test_cases: List[TestCase], output_file: str = "generated_test_cases.xlsx") -> str:
        data = []

        for tc in test_cases:
            data.append({
                "Test Case ID": tc.test_case_id,
                "Title": tc.title,
                "Scenario": tc.scenario,
                "Preconditions": " | ".join(tc.preconditions),
                "Steps": " -> ".join(tc.test_steps),
                "Expected Result": tc.expected_result,
                "Priority": tc.priority,
                "Type": tc.test_type,
                "Source AC": tc.source_criterion_id
            })

        df = pd.DataFrame(data)
        df.to_excel(output_file, index=False)

        return output_file