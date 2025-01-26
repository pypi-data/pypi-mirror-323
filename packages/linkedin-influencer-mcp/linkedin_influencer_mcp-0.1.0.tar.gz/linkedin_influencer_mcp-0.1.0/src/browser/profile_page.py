import logging

from playwright.async_api import Page

from src.browser.utils.utils import scrape_string_profile_info_using_llm
from src.models import ProfileInfo

logger = logging.getLogger(__name__)


class ProfilePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "https://www.linkedin.com/in"

    async def navigate_to_profile_page(self, linkedin_profile_id: str) -> None:
        """Navigate directly to a LinkedIn profile page."""
        try:
            profile_url = f"{self.base_url}/{linkedin_profile_id}/"
            logger.info(f"Navigating to profile: {profile_url}")
            await self.page.goto(profile_url, timeout=6000)
            # Wait for the main profile content to load
            await self.page.wait_for_selector("h1.inline", timeout=10000)
        except Exception as e:
            logger.error(
                f"Failed to navigate to profile '{linkedin_profile_id}': {str(e)}"
            )
            raise Exception(
                f"Failed to navigate to profile '{linkedin_profile_id}': {str(e)}"
            )

    async def get_profile_info(self, linkedin_profile_id) -> ProfileInfo:
        """Get profile information from the current page."""
        try:
            await self.navigate_to_profile_page(linkedin_profile_id)

            # Check visibility before getting elements
            basic_info_locator = self.page.locator(".mt2.relative")
            basic_info_visible = await basic_info_locator.is_visible()
            basic_info_html = (
                await basic_info_locator.all_inner_texts() if basic_info_visible else ""
            )

            about_locator = self.page.locator(".display-flex.ph5.pv3")
            about_visible = await about_locator.is_visible()
            about_html = await about_locator.all_inner_texts() if about_visible else ""

            profile_url = f"https://www.linkedin.com/in/{linkedin_profile_id}/"
            profile_id = f"linkedin_profile_id:{linkedin_profile_id}"
            user_info = f"""
            <Profile URL> {profile_url} </Profile URL>
            <Profile ID> {profile_id} </Profile ID>
            <Basic Info> {basic_info_html} </Basic Info>
            <Use as much of the About section as possible> <About> {about_html} </About> </Use as much of the About section as possible>
            """
            return await scrape_string_profile_info_using_llm(user_info)
        except Exception as e:
            logger.error(f"Failed to extract profile information: {str(e)}")
            raise Exception(f"Failed to extract profile information: {str(e)}")
