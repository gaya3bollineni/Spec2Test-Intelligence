from typing import List, Literal, Optional

from pydantic import BaseModel, Field


PlaywrightActionType = Literal[
    "goto",
    "click",
    "fill",
    "check",
    "uncheck",
    "select",
    "press",
    "assert_visible",
    "assert_text",
    "assert_url",
]

LocatorType = Literal[
    "role",
    "label",
    "placeholder",
    "text",
    "test_id",
    "css",
]


class PlaywrightLocator(BaseModel):
    locator_type: LocatorType
    value: str

    role_name: Optional[str] = None


class PlaywrightAction(BaseModel):
    action_type: PlaywrightActionType

    locator: Optional[PlaywrightLocator] = None

    value: Optional[str] = None

    description: Optional[str] = None


class PlaywrightTest(BaseModel):
    requirement_id: str
    test_case_id: str

    test_name: str

    scenario_type: str
    priority: str

    actions: List[PlaywrightAction] = Field(
        default_factory=list
    )

    expected_result: str

    source_criterion: str


class PlaywrightGenerationResult(BaseModel):
    tests: List[PlaywrightTest] = Field(
        default_factory=list
    )

    typescript_code: str

    generated_test_count: int = 0

    warnings: List[str] = Field(
        default_factory=list
    )