from src.ingestion.normalizer import InputNormalizer
from src.parsing.criteria_parser import CriteriaParser
from src.scenario_expander.expander import ScenarioExpander
from src.exporters.json_exporter import JSONExporter
from src.exporters.excel_exporter import ExcelExporter


def main():
    sample_input = """
    1. User should be able to log in with valid username and password.
    2. System should not allow login with invalid credentials.
    3. Error message should be shown when required fields are blank.
    4. Given the user is on the password reset page when the user enters a registered email then the reset link should be sent successfully.
    """

    normalizer = InputNormalizer()
    parser = CriteriaParser()
    expander = ScenarioExpander()
    json_exporter = JSONExporter()
    excel_exporter = ExcelExporter()

    normalized_items = normalizer.normalize(sample_input)
    parsed_items = parser.parse(normalized_items)
    test_cases = expander.generate(parsed_items)

    print("\n--- GENERATED TEST CASES ---")
    for tc in test_cases:
        print(tc.model_dump())

    json_file = json_exporter.export(test_cases)
    excel_file = excel_exporter.export(test_cases)

    print(f"\nJSON exported: {json_file}")
    print(f"Excel exported: {excel_file}")


if __name__ == "__main__":
    main()