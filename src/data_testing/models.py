from dataclasses import dataclass


@dataclass
class DataFieldRule:
    field_name: str
    data_type: str = "string"
    required: bool = False

    minimum: float | None = None
    maximum: float | None = None

    allowed_values: list[str] | None = None

    unique: bool = False


@dataclass
class DataTestScenario:
    test_id: str
    field_name: str
    test_type: str
    description: str
    expected_result: str