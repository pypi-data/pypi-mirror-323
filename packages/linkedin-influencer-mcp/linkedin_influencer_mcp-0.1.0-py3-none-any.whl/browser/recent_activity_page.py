"""Module for handling LinkedIn profile page interactions and data extraction."""

import asyncio
import logging
from typing import List, Union

from bs4 import BeautifulSoup
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class RecentActivityPage:
    """Handles LinkedIn profile page interactions and data extraction."""

    def __init__(self, page: Page):
        """Initialize ProfilePage with a Playwright page instance."""
        self.page = page
        self.base_url = "https://www.linkedin.com/in"

    async def scroll_page_for_content(self, scrolls: int = 2) -> None:
        """Scroll the page to load more content with improved handling."""
        try:
            previous_height = 0
            for _ in range(scrolls):
                current_height = await self.page.evaluate("document.body.scrollHeight")
                if current_height == previous_height:
                    break
                await self.page.evaluate(
                    "window.scrollTo(0, document.body.scrollHeight)"
                )
                await asyncio.sleep(2)
                previous_height = current_height
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error while scrolling: {str(e)}")
            raise

    @staticmethod
    def parse_html_content(page_source: str) -> List[BeautifulSoup]:
        """Parse HTML content to find post containers."""
        try:
            linkedin_soup = BeautifulSoup(page_source, "lxml")
            return [
                container
                for container in linkedin_soup.find_all(
                    "div", {"class": "feed-shared-update-v2"}
                )
                if "activity" in container.get("data-urn", "")
            ]
        except Exception as e:
            logger.error(f"Error parsing HTML content: {str(e)}")
            raise

    @staticmethod
    def extract_post_data(container: BeautifulSoup) -> dict:
        """Extract all post data from a container.

        Args:
            container: BeautifulSoup object containing post data

        Returns:
            dict: Post data including content and timestamp
        """
        try:
            content = ""
            timestamp = ""

            content_element = container.find("div", {"class": "update-components-text"})
            if content_element:
                content = content_element.text.strip()

            timestamp_element = container.find(
                "time", {"class": "artdeco-entity-lockup__caption"}
            )
            if timestamp_element:
                timestamp = timestamp_element.get_text().strip()

            return {"content": content, "timestamp": timestamp}
        except Exception as e:
            logger.error(f"Error extracting post data: {str(e)}")
            return {"content": "", "timestamp": ""}

    async def scrape_linkedin_posts(
        self, linkedin_profile_ids: Union[str, List[str]], max_posts: int = 5
    ) -> List[dict]:
        """Scrape posts from LinkedIn profiles with improved error handling and rate limiting."""
        profile_ids = (
            [linkedin_profile_ids]
            if isinstance(linkedin_profile_ids, str)
            else linkedin_profile_ids
        )
        all_posts = []

        for profile_id in profile_ids:
            try:
                logger.info(f"Starting to scrape profile: {profile_id}")

                # Add rate limiting between profiles
                if len(all_posts) > 0:
                    await asyncio.sleep(3)  # Delay between profiles

                await self.page.goto(
                    f"{self.base_url}/{profile_id}/recent-activity/all/", timeout=60000
                )

                # Wait for content to load
                try:
                    await self.page.wait_for_selector(
                        "div.feed-shared-update-v2", timeout=30000
                    )
                except Exception as e:
                    logger.error(f"No posts found for profile {profile_id}: {str(e)}")
                    continue

                await self.scroll_page_for_content()

                page_content = await self.page.content()
                containers = self.parse_html_content(page_content)

                profile_posts = []
                for container in containers[:max_posts]:
                    post_data = self.extract_post_data(container)
                    if post_data["content"]:  # Only add posts with content
                        post_data["profile_id"] = profile_id
                        profile_posts.append(post_data)

                all_posts.extend(profile_posts)
                logger.info(
                    f"Successfully scraped {len(profile_posts)} posts from {profile_id}"
                )
                logger.info(f"All posts: {all_posts}")

            except Exception as e:
                logger.error(f"Error scraping profile {profile_id}: {str(e)}")
                continue

        return all_posts

    async def navigate_to_profile_page(self, linkedin_profile_id: str) -> None:
        """Navigate directly to a LinkedIn profile page."""
        try:
            profile_url = f"{self.base_url}/{linkedin_profile_id}/"
            logger.info(f"Navigating to profile: {profile_url}")
            await self.page.goto(profile_url, timeout=60000)
            await self.page.wait_for_selector("h1.inline", timeout=10000)
        except Exception as e:
            logger.error(
                f"Failed to navigate to profile '{linkedin_profile_id}': {str(e)}"
            )
            raise
