"""Module for handling LinkedIn search functionality and profile interactions."""

import logging
from typing import Dict, List, Optional

from playwright.async_api import Page

from src.browser.profile_page import ProfilePage
from src.browser.search_page.search_page_helpers import (
    SearchPageInteractionHelper,
    SearchPageLocators,
)
from src.browser.utils.utils import get_custom_note, scrape_html_profile_info_using_llm
from src.models import ConnectionRequestResult, ProcessResult, ProfileInfo

logger = logging.getLogger(__name__)


class SearchPage:
    """Handles LinkedIn search page interactions and connection requests."""

    def __init__(self, page: Page):
        """Initialize SearchPage with required components."""
        self.page = page
        self._base_url = "https://www.linkedin.com/search/results/people"
        self._profile_page = ProfilePage(page)
        self.helper = SearchPageInteractionHelper(page)
        self._locators = SearchPageLocators()

    # Primary public interface
    async def send_connection_requests(
        self,
        search_query: str,
        max_connections: int,
        custom_note: bool,
        user_profile_id: str,
        location: str,
    ) -> tuple[list[ConnectionRequestResult], dict[str, int]] | list[str]:
        """Search for profiles and send connection requests."""
        try:
            user_info = await self.get_user_info(custom_note, user_profile_id)
            await self.navigate_to_search_results(search_query, location)

            results = []
            sent_requests = 0

            while sent_requests < max_connections:
                connect_buttons = await self.get_connect_buttons()

                if not connect_buttons:
                    if not await self.click_on_next_page():
                        break
                    continue

                process_result = await self._process_connect_buttons(
                    search_query=search_query,
                    buttons=connect_buttons[: max_connections - sent_requests],
                    custom_note=custom_note,
                    user_info=user_info,
                )

                results.extend(process_result.results)
                sent_requests += process_result.processed_count

                if sent_requests >= max_connections:
                    break

                if not await self.click_on_next_page():
                    break

            return (
                (results, {"total_requests_sent": len(results)})
                if results
                else ["Failed to send connection requests"]
            )

        except Exception as e:
            logger.error(f"Error sending connection requests: {str(e)}")
            return ["Failed to send connection requests"]

    # Navigation flows
    async def navigate_to_search_results(
        self, search_query: str, location: str
    ) -> None:
        """Navigate to LinkedIn search results for the given query."""
        try:
            await self.page.goto(f"{self._base_url}/?keywords={search_query}")
            await self.helper.wait_for_page_load()

            if location:
                await self.helper.select_location(location)
        except Exception as e:
            logger.error(f"Failed to navigate to search page: {str(e)}")
            raise

    async def click_on_next_page(self) -> bool:
        """Navigate to the next page of search results."""
        try:
            next_button = self.page.get_by_role("button", name="Next", exact=True)
            await self.page.wait_for_timeout(self.helper.timeouts.PAGE_LOAD)
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await next_button.click()
            await self.page.wait_for_timeout(self.helper.timeouts.NEXT_PAGE_LOAD)
            return True
        except Exception as e:
            raise Exception(f"Error navigating to next page: {str(e)}")

    # Connection request processing
    async def _process_connect_buttons(
        self,
        search_query: str,
        buttons: List,
        custom_note: bool,
        user_info: Optional[ProfileInfo],
    ) -> ProcessResult:
        """Process a batch of connect buttons."""
        results = []
        processed_count = 0

        for button in buttons:
            try:
                # Initialize profile_info
                profile_info = ProfileInfo()

                if custom_note:
                    profile_info = await self.extract_profile_info_from_button(button)
                    note = await get_custom_note(search_query, profile_info, user_info)
                else:
                    note = None

                connection_result = await self.click_connect_button(button, note)

                results.append(
                    ConnectionRequestResult(
                        status=connection_result["status"],
                        profile=profile_info,
                        note_sent=note or "",
                    )
                )

                processed_count += 1
                await self.page.wait_for_timeout(self.helper.timeouts.DEFAULT_DELAY)

            except Exception as e:
                logger.error(f"Error processing connection request: {str(e)}")
                raise

        return ProcessResult(results=results, processed_count=processed_count)

    async def click_connect_button(
        self, button, custom_note: str = None
    ) -> Dict[str, str]:
        """Initiate connection flow from a Connect button click."""
        try:
            await button.click()
            await self.helper.wait_for_default_delay()
            return (
                await self.click_send_button()
                if not custom_note
                else await self.send_note_and_connect(custom_note)
            )
        except Exception as e:
            logger.error(f"Error sending connection request: {str(e)}")
            raise

    async def click_send_button(self) -> Dict[str, str]:
        """Finalize connection request without note."""
        send_button = await self.helper.wait_for_selector_with_timeout(
            self._locators.SEND_BUTTON, "Send button not found after waiting"
        )
        await send_button.click()
        return {"status": "success"}

    async def send_note_and_connect(self, custom_note: str) -> Dict[str, str]:
        """Complete connection request with personalized note."""
        await self.helper.click_add_note_button()
        await self.helper.enter_custom_note(custom_note)
        await self.helper.wait_for_note_composition()
        return await self.helper.confirm_and_send_request()

    # Data extraction
    async def extract_profile_info_from_button(self, button) -> ProfileInfo:
        """Extract profile information from the connection button's parent card."""
        return await scrape_html_profile_info_using_llm(
            await button.evaluate(
                f"""
                (button) => button.closest('{self._locators.SEARCH_RESULT_CARD}')?.outerHTML
            """
            )
        )

    # Helper methods
    async def get_user_info(
        self, custom_note: bool, user_profile_id: str
    ) -> Optional[ProfileInfo]:
        """Fetch user info if custom note is required."""
        if not custom_note:
            return None
        user_info = await self._profile_page.get_profile_info(user_profile_id)
        logger.info(f"User info: {user_info}")
        return user_info

    async def get_connect_buttons(self) -> List:
        """Get connect buttons from current page."""
        await self.page.wait_for_timeout(self.helper.timeouts.BUTTON_INTERACTION)
        connect_buttons = await self.page.query_selector_all(
            self._locators.CONNECT_BUTTON
        )
        await self.page.wait_for_timeout(self.helper.timeouts.BUTTON_INTERACTION)

        logger.info(f"Found {len(connect_buttons)} connect buttons on the page.")
        return connect_buttons
