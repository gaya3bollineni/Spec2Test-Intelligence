from pydantic import BaseModel, Field
from typing import List, Optional


class RequirementItem(BaseModel):
    id: str
    raw_text: str
    normalized_text: str


class ParsedCriterion(BaseModel):
    id: str
    raw_text: str
    actor: Optional[str] = None
    action: Optional[str] = None
    condition: Optional[str] = None
    expected_outcome: Optional[str] = None
    rule_type: str = "functional"


class TestCase(BaseModel):
    test_case_id: str
    title: str
    scenario: str
    preconditions: List[str] = Field(default_factory=list)
    test_steps: List[str] = Field(default_factory=list)
    expected_result: str
    priority: str = "Medium"
    test_type: str = "Positive"
    source_criterion_id: str