from typing import Optional

from src.playwright.dom_models import (
    DOMElement,
)
from src.playwright.models import (
    PlaywrightLocator,
)


class DOMLocatorGenerator:
    """
    Selects a resilient Playwright locator for a
    matched DOM element.

    The ranking favors user-facing locators before
    implementation-specific CSS selectors.
    """

    def generate(
        self,
        element: DOMElement,
    ) -> Optional[PlaywrightLocator]:

        role = self._resolve_role(
            element
        )

        accessible_name = (
            element.label
            or element.aria_label
            or element.text
        )

        # Buttons and links are naturally represented
        # using accessible role + name.
        if (
            role in {"button", "link"}
            and accessible_name
        ):
            return PlaywrightLocator(
                locator_type="role",
                value=role,
                role_name=accessible_name,
            )

        # Form controls with explicit labels should
        # use Playwright's label locator.
        if element.label:
            return PlaywrightLocator(
                locator_type="label",
                value=element.label,
            )

        if element.aria_label:
            return PlaywrightLocator(
                locator_type="label",
                value=element.aria_label,
            )

        # Explicit test IDs are stable fallbacks.
        if element.test_id:
            return PlaywrightLocator(
                locator_type="test_id",
                value=element.test_id,
            )

        if element.placeholder:
            return PlaywrightLocator(
                locator_type="placeholder",
                value=element.placeholder,
            )

        # Visible link/button text can still provide
        # a useful user-facing locator.
        if element.text:
            return PlaywrightLocator(
                locator_type="text",
                value=element.text,
            )

        # CSS ID is intentionally a late fallback.
        if element.element_id:
            return PlaywrightLocator(
                locator_type="css",
                value=f"#{element.element_id}",
            )

        if element.name:
            escaped_name = (
                element.name.replace(
                    '"',
                    '\\"',
                )
            )

            return PlaywrightLocator(
                locator_type="css",
                value=(
                    f'[name="{escaped_name}"]'
                ),
            )

        return None

    @staticmethod
    def _resolve_role(
        element: DOMElement,
    ) -> Optional[str]:
        if element.role:
            return element.role

        if element.tag == "button":
            return "button"

        if element.tag == "a":
            return "link"

        if (
            element.tag == "input"
            and element.element_type
            in {
                "button",
                "submit",
                "reset",
            }
        ):
            return "button"

        if (
            element.tag == "input"
            and element.element_type
            == "checkbox"
        ):
            return "checkbox"

        if (
            element.tag == "input"
            and element.element_type
            == "radio"
        ):
            return "radio"

        return None