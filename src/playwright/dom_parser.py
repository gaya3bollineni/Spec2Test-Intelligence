from html.parser import HTMLParser
from typing import Optional

from src.playwright.dom_models import DOMElement, DOMParseResult


class _HTMLDOMCollector(HTMLParser):
    """Collect interactive elements, including open declarative shadow roots.

    This parses serialized HTML only. JavaScript-created shadow roots
    cannot be recovered from ordinary uploaded source HTML.
    """

    INTERACTIVE_TAGS = {"input", "button", "select", "textarea", "a"}
    TEST_ID_ATTRIBUTES = ("data-testid", "data-test-id", "data-test", "data-cy")
    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[DOMElement] = []
        self.warnings: list[str] = []
        # Frames preserve nesting for text capture and template handling.
        self.frames: list[dict] = []
        self.shadow_path: list[str] = []
        # IDs and labels are scoped to their DOM tree, not globally.
        self.labels_by_scope: dict[tuple[str, ...], dict[str, str]] = {}
        self.element_scopes: list[tuple[str, ...]] = []
        self.skipped_template_depth = 0

    @staticmethod
    def _clean_text(value: str) -> str:
        return " ".join(value.split()).strip()

    @staticmethod
    def _host_name(tag: str, attributes: dict[str, str]) -> str:
        # A host ID makes nested paths easier to distinguish.
        return f"{tag}#{attributes['id']}" if attributes.get("id") else tag

    def _test_id(self, attributes: dict[str, str]) -> Optional[str]:
        return next(
            (attributes[key] for key in self.TEST_ID_ATTRIBUTES if attributes.get(key)),
            None,
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        attributes = {key.lower(): value or "" for key, value in attrs}

        if self.skipped_template_depth:
            if tag == "template":
                self.skipped_template_depth += 1
            return

        if tag == "template":
            mode = attributes.get("shadowrootmode", "").lower()
            if mode == "open":
                host = next(
                    (frame for frame in reversed(self.frames) if frame["tag"] != "template"),
                    None,
                )
                if host is None:
                    self.warnings.append("Open shadow template has no identifiable host; skipped.")
                    self.skipped_template_depth = 1
                    return
                self.shadow_path.append(host["host_name"])
                self.frames.append({"tag": "template", "shadow": True, "text": []})
            else:
                if mode == "closed":
                    self.warnings.append("Closed declarative shadow root skipped.")
                # Ordinary templates are inert; don't report their controls.
                self.skipped_template_depth = 1
            return

        frame = {
            "tag": tag,
            "host_name": self._host_name(tag, attributes),
            "text": [],
            "element_index": None,
            "label_for": attributes.get("for") if tag == "label" else None,
            "scope": tuple(self.shadow_path),
        }
        if tag in self.INTERACTIVE_TAGS:
            element = DOMElement(
                tag=tag,
                element_type=attributes.get("type") or None,
                element_id=attributes.get("id") or None,
                name=attributes.get("name") or None,
                placeholder=attributes.get("placeholder") or None,
                test_id=self._test_id(attributes),
                role=attributes.get("role") or None,
                value=attributes.get("value") or None,
                href=attributes.get("href") or None,
                aria_label=attributes.get("aria-label") or None,
                classes=attributes.get("class", "").split(),
                attributes=attributes,
                shadow_host_path=list(self.shadow_path),
                inside_shadow_dom=bool(self.shadow_path),
            )
            self.elements.append(element)
            self.element_scopes.append(tuple(self.shadow_path))
            frame["element_index"] = len(self.elements) - 1

        if tag in self.VOID_TAGS:
            self._finish_frame(frame)
        else:
            self.frames.append(frame)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID_TAGS:
            self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if self.skipped_template_depth:
            return
        text = self._clean_text(data)
        if text:
            for frame in self.frames:
                # Do not allow shadow-tree text to become host light-DOM text.
                if frame["tag"] == "template":
                    continue
                if frame.get("scope") == tuple(self.shadow_path):
                    frame["text"].append(text)

    def _finish_frame(self, frame: dict) -> None:
        text = self._clean_text(" ".join(frame.get("text", [])))
        index = frame.get("element_index")
        if index is not None and text:
            self.elements[index].text = text
        label_for = frame.get("label_for")
        if label_for and text:
            self.labels_by_scope.setdefault(frame["scope"], {})[label_for] = text

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.skipped_template_depth:
            if tag == "template":
                self.skipped_template_depth -= 1
            return
        if not self.frames:
            return
        # HTMLParser does not validate nesting. Ignore unmatched closing tags.
        match = next(
            (i for i in range(len(self.frames) - 1, -1, -1)
             if self.frames[i]["tag"] == tag),
            None,
        )
        if match is None:
            return
        while len(self.frames) > match:
            frame = self.frames.pop()
            if frame.get("shadow"):
                self.shadow_path.pop()
            else:
                self._finish_frame(frame)

    def apply_labels(self) -> None:
        for element, scope in zip(self.elements, self.element_scopes):
            if element.element_id:
                element.label = self.labels_by_scope.get(scope, {}).get(element.element_id)
            if not element.label and element.aria_label:
                element.label = element.aria_label


class DOMParser:
    """Parse uploaded HTML without generating Playwright locators."""

    def parse(self, html: str) -> DOMParseResult:
        if not html or not html.strip():
            return DOMParseResult(warnings=["No HTML content was provided."])
        collector = _HTMLDOMCollector()
        try:
            collector.feed(html)
            collector.close()
            # Finish any open frames in incomplete but recoverable HTML.
            while collector.frames:
                frame = collector.frames.pop()
                if frame.get("shadow"):
                    if collector.shadow_path:
                        collector.shadow_path.pop()
                else:
                    collector._finish_frame(frame)
        except Exception as exc:
            return DOMParseResult(warnings=[f"HTML could not be fully parsed: {exc}"])
        collector.apply_labels()
        warnings = collector.warnings.copy()
        if not collector.elements:
            warnings.append("No supported interactive elements were found.")
        return DOMParseResult(
            elements=collector.elements,
            interactive_element_count=len(collector.elements),
            warnings=warnings,
        )
