"""Helper methods for LinkedIn interactions."""

import logging
from typing import Dict

from playwright.async_api import Page

logger = logging.getLogger(__name__)


class SearchPageLocators:
    """Centralized locators for LinkedIn elements."""

    def __init__(self):
        self.SEARCH_RESULT_CARD = (
            '[data-view-name="search-entity-result-universal-template"]'
        )
        self.CONNECT_BUTTON = "button:has-text('Connect')"
        self.SEND_BUTTON = "button:has-text('Send')"
        self.ADD_NOTE_BUTTON = "button:has-text('Add a note')"
        self.NOTE_TEXTAREA = "textarea[name='message']"
        self.NEXT_PAGE_BUTTON = "button[aria-label='Next']"
        self.LOCATIONS_DROPDOWN = "Locations filter. Clicking this button displays all Locations filter options."
        self.ADD_A_LOCATION_TEXT_BOX_PLACEHOLDER = "Add a location"


class LinkedInTimeouts:
    """Centralized timeout values for LinkedIn interactions."""

    def __init__(self):
        self.PAGE_LOAD = 2000
        self.BUTTON_INTERACTION = 1000
        self.NOTE_COMPOSITION = 500
        self.SEND_CONFIRMATION = 1000
        self.DEFAULT_DELAY = 100
        self.CUSTOM_NOTE_PAUSE = 300
        self.NEXT_PAGE_LOAD = 1000


class SearchPageInteractionHelper:
    """Helper class for common LinkedIn page interactions."""

    def __init__(self, page: Page):
        self.page = page
        self._locators = SearchPageLocators()
        self.timeouts = LinkedInTimeouts()

    # Timeout management helpers
    async def wait_for_page_load(self):
        await self.page.wait_for_timeout(self.timeouts.PAGE_LOAD)

    async def wait_for_default_delay(self):
        await self.page.wait_for_timeout(self.timeouts.DEFAULT_DELAY)

    async def wait_for_note_composition(self):
        await self.page.wait_for_timeout(self.timeouts.NOTE_COMPOSITION)

    async def wait_for_send_confirmation(self):
        await self.page.wait_for_timeout(self.timeouts.SEND_CONFIRMATION)

    async def wait_for_selector_with_timeout(self, selector, error_message):
        element = await self.page.wait_for_selector(
            selector, timeout=self.timeouts.BUTTON_INTERACTION
        )
        if not element:
            raise ValueError(error_message)
        return element

    # Button interaction helpers
    async def click_add_note_button(self):
        add_note_button = await self.wait_for_selector_with_timeout(
            self._locators.ADD_NOTE_BUTTON, "Add note button not found"
        )
        await add_note_button.click()

    async def enter_custom_note(self, note_text: str):
        await self.page.fill(self._locators.NOTE_TEXTAREA, note_text)

    async def confirm_and_send_request(self) -> Dict[str, str]:
        send_button = await self.wait_for_selector_with_timeout(
            self._locators.SEND_BUTTON, "Send button missing after note entry"
        )
        await self.wait_for_send_confirmation()
        await send_button.click()
        return {"status": "success"}

    async def select_location(self, location: str):
        try:
            # Wait for the dropdown to be visible first
            location_button = self.page.get_by_role(
                "button", name=self._locators.LOCATIONS_DROPDOWN, exact=True
            )
            await location_button.wait_for(state="visible")

            # Click to open the dropdown
            await location_button.click()
            await self.wait_for_default_delay()

            # Fill in the location
            await self.page.get_by_placeholder(
                self._locators.ADD_A_LOCATION_TEXT_BOX_PLACEHOLDER
            ).fill(location)
            await self.wait_for_default_delay()

            # Wait for and select the first location suggestion
            await self.page.wait_for_selector(
                ".basic-typeahead__selectable", state="visible"
            )
            await self.page.click(".basic-typeahead__selectable >> nth=0")

            # Wait for and click the "Show results" button
            await self.page.get_by_role("button", name="Show results").click()
            await self.wait_for_page_load()

        except Exception as e:
            logger.error(f"Failed to select location: {str(e)}")
            raise
