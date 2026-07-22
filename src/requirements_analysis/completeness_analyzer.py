from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.models.schemas import ParsedCriterion


@dataclass
class CompletenessCheck:
    name: str
    is_present: bool
    message: str


@dataclass
class CriterionCompletenessResult:
    criterion_id: str
    criterion_text: str
    completeness_score: int
    checks: List[CompletenessCheck] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CompletenessAnalysisResult:
    overall_score: int
    complete_criteria_count: int
    incomplete_criteria_count: int
    criterion_results: List[CriterionCompletenessResult] = field(
        default_factory=list
    )


class CompletenessAnalyzer:
    EXPECTED_RESULT_WORDS = {
        "then",
        "successfully",
        "redirect",
        "redirected",
        "display",
        "displayed",
        "show",
        "shown",
        "receive",
        "received",
        "created",
        "generated",
        "completed",
        "saved",
        "updated",
        "approved",
        "rejected",
        "sent",
    }

    VALIDATION_WORDS = {
        "display",
        "show",
        "return",
        "reject",
        "allow",
        "deny",
        "generate",
        "send",
        "redirect",
        "create",
        "save",
        "update",
        "error",
        "message",
        "confirmation",
    }

    PRECONDITION_WORDS = {
        "given",
        "when",
        "if",
        "while",
        "after",
        "before",
        "with",
        "using",
    }

    def analyze(
        self,
        parsed_criteria: List[ParsedCriterion],
    ) -> CompletenessAnalysisResult:
        criterion_results = []

        for criterion in parsed_criteria:
            result = self.analyze_criterion(criterion)
            criterion_results.append(result)

        if not criterion_results:
            return CompletenessAnalysisResult(
                overall_score=0,
                complete_criteria_count=0,
                incomplete_criteria_count=0,
                criterion_results=[],
            )

        overall_score = round(
            sum(
                result.completeness_score
                for result in criterion_results
            )
            / len(criterion_results)
        )

        complete_count = sum(
            result.completeness_score == 100
            for result in criterion_results
        )

        return CompletenessAnalysisResult(
            overall_score=overall_score,
            complete_criteria_count=complete_count,
            incomplete_criteria_count=(
                len(criterion_results) - complete_count
            ),
            criterion_results=criterion_results,
        )

    def analyze_criterion(
        self,
        criterion: ParsedCriterion,
    ) -> CriterionCompletenessResult:
        text = criterion.raw_text.strip()
        lower_text = text.lower()

        actor_present = bool(criterion.actor)
        action_present = bool(criterion.action)

        expected_result_present = bool(
            criterion.expected_outcome
            and criterion.expected_outcome.strip()
            and criterion.expected_outcome.strip() != text
        ) or any(
            word in lower_text
            for word in self.EXPECTED_RESULT_WORDS
        )

        validation_present = any(
            word in lower_text
            for word in self.VALIDATION_WORDS
        )

        precondition_present = bool(
            criterion.condition
        ) or any(
            word in lower_text
            for word in self.PRECONDITION_WORDS
        )

        checks = [
            CompletenessCheck(
                name="Actor",
                is_present=actor_present,
                message=(
                    f"Actor identified: {criterion.actor}"
                    if actor_present
                    else "Actor is missing."
                ),
            ),
            CompletenessCheck(
                name="Action",
                is_present=action_present,
                message=(
                    f"Action identified: {criterion.action}"
                    if action_present
                    else "Action is missing."
                ),
            ),
            CompletenessCheck(
                name="Expected Result",
                is_present=expected_result_present,
                message=(
                    "Expected result identified."
                    if expected_result_present
                    else "Expected result is missing."
                ),
            ),
            CompletenessCheck(
                name="Validation Criteria",
                is_present=validation_present,
                message=(
                    "Validation criteria identified."
                    if validation_present
                    else "Validation criteria are missing."
                ),
            ),
            CompletenessCheck(
                name="Preconditions",
                is_present=precondition_present,
                message=(
                    "Preconditions or triggering conditions identified."
                    if precondition_present
                    else "Preconditions are not specified."
                ),
            ),
        ]

        score = sum(
            20
            for check in checks
            if check.is_present
        )

        recommendations = []

        if not actor_present:
            recommendations.append(
                "Specify who performs the action, such as User, Customer, "
                "Administrator, Agent, or System."
            )

        if not action_present:
            recommendations.append(
                "Specify the action or behavior that must occur."
            )

        if not expected_result_present:
            recommendations.append(
                "Specify what should happen after the action is completed."
            )

        if not validation_present:
            recommendations.append(
                "Define an observable result such as a confirmation message, "
                "status update, redirect, generated identifier, or error."
            )

        if not precondition_present:
            recommendations.append(
                "Add the starting condition, such as an active account, "
                "valid credentials, required permissions, or existing data."
            )

        return CriterionCompletenessResult(
            criterion_id=criterion.id,
            criterion_text=text,
            completeness_score=score,
            checks=checks,
            recommendations=recommendations,
        )