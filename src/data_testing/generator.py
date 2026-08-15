from src.data_testing.models import (
    DataFieldRule,
    DataTestScenario,
)


class DataTestGenerator:

    def generate(
        self,
        rules: list[DataFieldRule],
    ) -> list[DataTestScenario]:

        scenarios: list[DataTestScenario] = []

        counter = 1

        for rule in rules:

            scenarios.append(
                DataTestScenario(
                    test_id=f"DT-{counter:03d}",
                    field_name=rule.field_name,
                    test_type="Data Type",
                    description=(
                        f"Validate {rule.field_name} "
                        f"contains {rule.data_type} values."
                    ),
                    expected_result=(
                        f"{rule.field_name} should contain "
                        f"only valid {rule.data_type} values."
                    ),
                )
            )

            counter += 1

            if rule.required:
                scenarios.append(
                    DataTestScenario(
                        test_id=f"DT-{counter:03d}",
                        field_name=rule.field_name,
                        test_type="Null Validation",
                        description=(
                            f"Validate {rule.field_name} "
                            "does not contain null values."
                        ),
                        expected_result=(
                            f"{rule.field_name} must be populated."
                        ),
                    )
                )

                counter += 1

            if (
                rule.minimum is not None
                or rule.maximum is not None
            ):
                scenarios.append(
                    DataTestScenario(
                        test_id=f"DT-{counter:03d}",
                        field_name=rule.field_name,
                        test_type="Boundary",
                        description=(
                            f"Validate boundary values for "
                            f"{rule.field_name}."
                        ),
                        expected_result=(
                            f"{rule.field_name} should remain "
                            "within the configured range."
                        ),
                    )
                )

                counter += 1

            if rule.allowed_values:
                scenarios.append(
                    DataTestScenario(
                        test_id=f"DT-{counter:03d}",
                        field_name=rule.field_name,
                        test_type="Allowed Values",
                        description=(
                            f"Validate accepted values for "
                            f"{rule.field_name}."
                        ),
                        expected_result=(
                            f"{rule.field_name} should contain "
                            "only configured allowed values."
                        ),
                    )
                )

                counter += 1

            if rule.unique:
                scenarios.append(
                    DataTestScenario(
                        test_id=f"DT-{counter:03d}",
                        field_name=rule.field_name,
                        test_type="Duplicate Validation",
                        description=(
                            f"Validate duplicate values do not "
                            f"exist for {rule.field_name}."
                        ),
                        expected_result=(
                            f"{rule.field_name} values should "
                            "remain unique."
                        ),
                    )
                )

                counter += 1

        return scenarios