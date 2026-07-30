from src.ingestion.normalizer import InputNormalizer


def test_manual_input_generates_requirement_ids() -> None:
    normalizer = InputNormalizer()

    requirements = normalizer.normalize(
        """
        1. User can log in with valid credentials.
        2. User can reset the password.
        """
    )

    assert len(requirements) == 2
    assert requirements[0].id == "AC-001"
    assert requirements[1].id == "AC-002"


def test_manual_input_defaults_priority_to_medium() -> None:
    normalizer = InputNormalizer()

    requirements = normalizer.normalize(
        "User can log in with valid credentials."
    )

    assert len(requirements) == 1
    assert requirements[0].priority == "Medium"


def test_manual_input_removes_extra_whitespace() -> None:
    normalizer = InputNormalizer()

    requirements = normalizer.normalize(
        "User   can    submit   the application."
    )

    assert requirements[0].normalized_text == (
        "User can submit the application."
    )


def test_structured_records_preserve_ids_and_priorities() -> None:
    normalizer = InputNormalizer()

    records = [
        {
            "requirement_id": "REQ-101",
            "acceptance_criteria": (
                "Customer can submit a valid application."
            ),
            "priority": "Critical",
        },
        {
            "requirement_id": "REQ-102",
            "acceptance_criteria": (
                "Customer can update the application."
            ),
            "priority": "High",
        },
    ]

    requirements = normalizer.normalize_records(records)

    assert len(requirements) == 2

    assert requirements[0].id == "REQ-101"
    assert requirements[0].priority == "Critical"

    assert requirements[1].id == "REQ-102"
    assert requirements[1].priority == "High"


def test_structured_records_generate_missing_id() -> None:
    normalizer = InputNormalizer()

    records = [
        {
            "requirement_id": "",
            "acceptance_criteria": (
                "User can download the report."
            ),
            "priority": "Low",
        }
    ]

    requirements = normalizer.normalize_records(records)

    assert requirements[0].id == "REQ-001"
    assert requirements[0].priority == "Low"


def test_structured_records_default_missing_priority() -> None:
    normalizer = InputNormalizer()

    records = [
        {
            "requirement_id": "REQ-201",
            "acceptance_criteria": (
                "Admin can delete an inactive account."
            ),
            "priority": "",
        }
    ]

    requirements = normalizer.normalize_records(records)

    assert requirements[0].priority == "Medium"


def test_empty_acceptance_criteria_is_ignored() -> None:
    normalizer = InputNormalizer()

    records = [
        {
            "requirement_id": "REQ-301",
            "acceptance_criteria": "",
            "priority": "High",
        },
        {
            "requirement_id": "REQ-302",
            "acceptance_criteria": (
                "User can search for an application."
            ),
            "priority": "Medium",
        },
    ]

    requirements = normalizer.normalize_records(records)

    assert len(requirements) == 1
    assert requirements[0].id == "REQ-302"