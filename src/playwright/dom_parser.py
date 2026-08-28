from html.parser import HTMLParser
from typing import Optional

from src.playwright.dom_models import (
    DOMElement,
    DOMParseResult,
)


class _HTMLDOMCollector(HTMLParser):
    """
    Low-level HTML collector used internally by
    DOMParser.

    Only potentially useful interactive elements
    are retained.
    """

    INTERACTIVE_TAGS = {
        "input",
        "button",
        "select",
        "textarea",
        "a",
    }

    TEST_ID_ATTRIBUTES = (
        "data-testid",
        "data-test-id",
        "data-test",
        "data-cy",
    )

    def __init__(self) -> None:
        super().__init__()

        self.elements: list[DOMElement] = []

        self.labels_by_for: dict[
            str,
            str,
        ] = {}

        self.current_label_for: Optional[
            str
        ] = None

        self.current_label_text: list[
            str
        ] = []

        self.current_element_index: Optional[
            int
        ] = None

        self.current_text_parts: list[
            str
        ] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[
            tuple[str, Optional[str]]
        ],
    ) -> None:
        tag = tag.lower()

        attributes = {
            key.lower(): value or ""
            for key, value in attrs
        }

        if tag == "label":
            self.current_label_for = (
                attributes.get("for")
                or None
            )

            self.current_label_text = []

            return

        if tag not in self.INTERACTIVE_TAGS:
            return

        test_id = self._find_test_id(
            attributes
        )

        classes = [
            item
            for item in (
                attributes
                .get("class", "")
                .split()
            )
            if item
        ]

        element = DOMElement(
            tag=tag,
            element_type=(
                attributes.get("type")
                or None
            ),
            element_id=(
                attributes.get("id")
                or None
            ),
            name=(
                attributes.get("name")
                or None
            ),
            placeholder=(
                attributes.get(
                    "placeholder"
                )
                or None
            ),
            test_id=test_id,
            role=(
                attributes.get("role")
                or None
            ),
            value=(
                attributes.get("value")
                or None
            ),
            href=(
                attributes.get("href")
                or None
            ),
            aria_label=(
                attributes.get(
                    "aria-label"
                )
                or None
            ),
            classes=classes,
            attributes=attributes,
        )

        self.elements.append(
            element
        )

        if tag in {
            "button",
            "a",
            "select",
            "textarea",
        }:
            self.current_element_index = (
                len(self.elements) - 1
            )

            self.current_text_parts = []

        else:
            self.current_element_index = None
            self.current_text_parts = []

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        tag = tag.lower()

        if tag == "label":
            label_text = self._clean_text(
                " ".join(
                    self.current_label_text
                )
            )

            if (
                self.current_label_for
                and label_text
            ):
                self.labels_by_for[
                    self.current_label_for
                ] = label_text

            self.current_label_for = None
            self.current_label_text = []

            return

        if (
            self.current_element_index
            is not None
            and tag
            == self.elements[
                self.current_element_index
            ].tag
        ):
            text = self._clean_text(
                " ".join(
                    self.current_text_parts
                )
            )

            if text:
                self.elements[
                    self.current_element_index
                ].text = text

            self.current_element_index = None
            self.current_text_parts = []

    def handle_data(
        self,
        data: str,
    ) -> None:
        text = self._clean_text(
            data
        )

        if not text:
            return

        if self.current_label_for is not None:
            self.current_label_text.append(
                text
            )

        if (
            self.current_element_index
            is not None
        ):
            self.current_text_parts.append(
                text
            )

    def apply_labels(
        self,
    ) -> None:
        for element in self.elements:
            if (
                element.element_id
                and element.element_id
                in self.labels_by_for
            ):
                element.label = (
                    self.labels_by_for[
                        element.element_id
                    ]
                )

            elif element.aria_label:
                element.label = (
                    element.aria_label
                )

    def _find_test_id(
        self,
        attributes: dict[str, str],
    ) -> Optional[str]:
        for attribute_name in (
            self.TEST_ID_ATTRIBUTES
        ):
            value = attributes.get(
                attribute_name
            )

            if value:
                return value

        return None

    @staticmethod
    def _clean_text(
        value: str,
    ) -> str:
        return " ".join(
            value.split()
        ).strip()


class DOMParser:
    """
    Converts uploaded HTML into structured DOM
    elements that can later be matched against
    automation intent.

    This parser intentionally does not generate
    Playwright locators. Locator selection belongs
    to the locator-ranking layer.
    """

    def parse(
        self,
        html: str,
    ) -> DOMParseResult:
        warnings: list[str] = []

        if not html or not html.strip():
            return DOMParseResult(
                warnings=[
                    "No HTML content was provided."
                ]
            )

        collector = _HTMLDOMCollector()

        try:
            collector.feed(
                html
            )

            collector.close()

        except Exception as exc:
            return DOMParseResult(
                warnings=[
                    (
                        "HTML could not be fully "
                        f"parsed: {exc}"
                    )
                ]
            )

        collector.apply_labels()

        if not collector.elements:
            warnings.append(
                (
                    "No supported interactive "
                    "elements were found."
                )
            )

        return DOMParseResult(
            elements=collector.elements,
            interactive_element_count=len(
                collector.elements
            ),
            warnings=warnings,
        )