from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineResult:
    test_cases: list[Any] = field(default_factory=list)
    parsed_items: list[Any] = field(default_factory=list)

    requirement_analysis: Any = None
    completeness_analysis: Any = None

    traceability_rows: list[Any] = field(default_factory=list)

    duplicate_requirements: list[Any] = field(default_factory=list)
    conflicting_requirements: list[Any] = field(default_factory=list)
    dependencies: list[Any] = field(default_factory=list)

    health_scores: list[Any] = field(default_factory=list)