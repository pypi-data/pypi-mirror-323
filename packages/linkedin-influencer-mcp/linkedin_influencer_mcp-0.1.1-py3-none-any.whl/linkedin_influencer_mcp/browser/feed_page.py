"""Module for handling LinkedIn feed page interactions and post creation."""

import asyncio
import logging

from playwright.async_api import Page, TimeoutError

logger = logging.getLogger(__name__)


class FeedPage:
    """Handles LinkedIn feed page interactions and post creation functionality."""

    def __init__(self, page: Page):
        """Initialize FeedPage with a Playwright page instance.

        Args:
            page: Playwright Page object for browser interaction
        """
        self.page = page
        self._start_post_button = page.get_by_role("button", name="Start a post")
        self._post_text_area = page.locator(
            '.ql-editor[data-placeholder="Share your thoughts…"]'
        )
        self._post_button = page.locator(
            ".share-box_actions button.artdeco-button--primary"
        )

    async def _click_start_post(self):
        """Click the start post button to open post creation modal."""
        try:
            await self._start_post_button.click()
            logger.info("Successfully clicked start post button")
        except TimeoutError as e:
            logger.error("Failed to open post creation modal: Timeout")
            raise Exception("Failed to open post creation modal: Timeout") from e

    async def create_post(self, content: str) -> bool:
        """Create a new LinkedIn post with the given content.

        Args:
            content (str): The text content to post

        Returns:
            bool: True if post was created successfully

        Raises:
            Exception: If post creation fails
        """
        try:
            await self._click_start_post()
            await self._post_text_area.fill(content)
            await self._post_button.click()
            await asyncio.sleep(2)  # Wait for post to be created
            logger.info("Successfully created LinkedIn post")
            return True
        except TimeoutError as e:
            logger.error(f"Failed to create post: {str(e)}")
            raise Exception("Failed to create post: Timeout") from e
        except Exception as e:
            logger.error(f"Unexpected error creating post: {str(e)}")
            raise

    async def _wait_for_feed_load(self):
        """Wait for the LinkedIn feed to load."""
        try:
            await self.page.wait_for_selector(
                ".feed-shared-update-v2", state="visible", timeout=15000
            )
            logger.info("Feed loaded successfully")
        except TimeoutError as e:
            logger.error("Feed failed to load: Timeout")
            raise Exception("Feed failed to load: Timeout") from e
