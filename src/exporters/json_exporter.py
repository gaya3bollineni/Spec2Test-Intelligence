import json
from typing import List
from src.models.schemas import TestCase


class JSONExporter:
    def export(self, test_cases: List[TestCase], output_file: str = "generated_test_cases.json") -> str:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump([tc.model_dump() for tc in test_cases], file, indent=2)

        return output_file