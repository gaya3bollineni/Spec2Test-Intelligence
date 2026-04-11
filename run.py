from src.ingestion.normalizer import InputNormalizer
from src.parsing.criteria_parser import CriteriaParser


def main():
    sample_input = """
    1. User should be able to log in with valid username and password.
    2. System should not allow login with invalid credentials.
    3. Error message should be shown when required fields are blank.
    4. Given the user is on the password reset page when the user enters a registered email then the reset link should be sent successfully.
    """

    normalizer = InputNormalizer()
    parser = CriteriaParser()

    normalized_items = normalizer.normalize(sample_input)
    parsed_items = parser.parse(normalized_items)

    print("\n--- NORMALIZED ITEMS ---")
    for item in normalized_items:
        print(item.model_dump())

    print("\n--- PARSED CRITERIA ---")
    for parsed in parsed_items:
        print(parsed.model_dump())


if __name__ == "__main__":
    main()