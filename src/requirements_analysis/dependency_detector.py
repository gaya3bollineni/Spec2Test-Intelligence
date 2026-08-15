from dataclasses import dataclass
from typing import List

from src.models.schemas import ParsedCriterion


@dataclass
class RequirementDependency:
    requirement_id: str
    depends_on: str
    requirement_text: str
    dependency_text: str
    reason: str


class RequirementDependencyDetector:
    """
    Detects simple potential requirement dependencies
    using deterministic keyword relationships.
    """

    DEPENDENCY_RULES = [
        {
            "source_keywords": [
                "dashboard",
                "home page",
                "profile",
                "account",
            ],
            "dependency_keywords": [
                "login",
                "log in",
                "authenticate",
                "authenticated",
            ],
            "reason": (
                "This requirement appears to require an authenticated "
                "user state established by another requirement."
            ),
        },
        {
            "source_keywords": [
                "download report",
                "view report",
                "export report",
            ],
            "dependency_keywords": [
                "dashboard",
                "report available",
                "generate report",
            ],
            "reason": (
                "This requirement appears to depend on the report "
                "or dashboard being available first."
            ),
        },
        {
            "source_keywords": [
                "submit application",
                "submit loan application",
            ],
            "dependency_keywords": [
                "create application",
                "enter application",
                "complete application",
            ],
            "reason": (
                "Submission appears to depend on an application "
                "being created or completed first."
            ),
        },
        {
            "source_keywords": [
                "approve application",
                "reject application",
                "loan decision",
            ],
            "dependency_keywords": [
                "submit application",
                "submit loan application",
            ],
            "reason": (
                "The decision requirement appears to depend on "
                "an application being submitted first."
            ),
        },
    ]

    def detect(
        self,
        parsed_items: List[ParsedCriterion],
    ) -> List[RequirementDependency]:
        dependencies: List[RequirementDependency] = []

        for requirement in parsed_items:
            for candidate in parsed_items:
                if requirement.id == candidate.id:
                    continue

                dependency_reason = self._find_dependency(
                    requirement.raw_text,
                    candidate.raw_text,
                )

                if dependency_reason:
                    dependencies.append(
                        RequirementDependency(
                            requirement_id=requirement.id,
                            depends_on=candidate.id,
                            requirement_text=requirement.raw_text,
                            dependency_text=candidate.raw_text,
                            reason=dependency_reason,
                        )
                    )

        return dependencies

    def _find_dependency(
        self,
        requirement_text: str,
        candidate_text: str,
    ) -> str | None:
        requirement_lower = requirement_text.lower()
        candidate_lower = candidate_text.lower()

        for rule in self.DEPENDENCY_RULES:
            source_match = any(
                keyword in requirement_lower
                for keyword in rule["source_keywords"]
            )

            dependency_match = any(
                keyword in candidate_lower
                for keyword in rule["dependency_keywords"]
            )

            if source_match and dependency_match:
                return rule["reason"]

        return None