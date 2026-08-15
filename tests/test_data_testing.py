from src.data_testing.generator import (
    DataTestGenerator,
)
from src.data_testing.models import (
    DataFieldRule,
)


def test_required_field_generates_null_test() -> None:

    rules = [
        DataFieldRule(
            field_name="Customer ID",
            data_type="string",
            required=True,
        )
    ]

    scenarios = (
        DataTestGenerator().generate(
            rules
        )
    )

    types = {
        scenario.test_type
        for scenario in scenarios
    }

    assert "Data Type" in types
    assert "Null Validation" in types


def test_numeric_range_generates_boundary_test() -> None:

    rules = [
        DataFieldRule(
            field_name="Credit Score",
            data_type="integer",
            minimum=300,
            maximum=850,
        )
    ]

    scenarios = (
        DataTestGenerator().generate(
            rules
        )
    )

    assert any(
        scenario.test_type == "Boundary"
        for scenario in scenarios
    )


def test_unique_field_generates_duplicate_test() -> None:

    rules = [
        DataFieldRule(
            field_name="Customer ID",
            data_type="string",
            unique=True,
        )
    ]

    scenarios = (
        DataTestGenerator().generate(
            rules
        )
    )

    assert any(
        scenario.test_type
        == "Duplicate Validation"
        for scenario in scenarios
    )