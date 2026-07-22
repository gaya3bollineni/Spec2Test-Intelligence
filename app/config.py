APP_NAME = "Spec2Test Intelligence"

APP_ICON = "🧪"

APP_DESCRIPTION = (
    "Analyze acceptance criteria and generate structured, "
    "traceable QA test cases."
)

SUPPORTED_SCENARIO_TYPES = [
    "Positive",
    "Negative",
    "Edge",
]

SAMPLE_ACCEPTANCE_CRITERIA = """1. User should be able to log in with valid username and password.
2. System should not allow login with invalid credentials.
3. Error message should be shown when required fields are blank.
4. Given the user is on the password reset page when the user enters a registered email then the reset link should be sent successfully.
"""

ACCEPTANCE_CRITERIA_PLACEHOLDER = """Paste acceptance criteria here.

Example:
1. User should be able to log in with valid credentials.
2. System should reject invalid credentials.
"""

EXCEL_SHEET_NAME = "Generated Test Cases"

JSON_FILE_NAME = "generated_test_cases.json"

EXCEL_FILE_NAME = "generated_test_cases.xlsx"