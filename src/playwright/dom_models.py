from typing import List, Optional

from pydantic import BaseModel, Field


class DOMElement(BaseModel):
    """
    Structured representation of an interactive
    element discovered in uploaded HTML.
    """

    tag: str

    element_type: Optional[str] = None

    element_id: Optional[str] = None

    name: Optional[str] = None

    label: Optional[str] = None

    placeholder: Optional[str] = None

    test_id: Optional[str] = None

    role: Optional[str] = None

    text: Optional[str] = None

    value: Optional[str] = None

    href: Optional[str] = None

    aria_label: Optional[str] = None

    classes: List[str] = Field(
        default_factory=list
    )

    attributes: dict[str, str] = Field(
        default_factory=dict
    )


class DOMParseResult(BaseModel):
    """
    Result returned by the DOM parser.
    """

    elements: List[DOMElement] = Field(
        default_factory=list
    )

    interactive_element_count: int = 0

    warnings: List[str] = Field(
        default_factory=list
    )