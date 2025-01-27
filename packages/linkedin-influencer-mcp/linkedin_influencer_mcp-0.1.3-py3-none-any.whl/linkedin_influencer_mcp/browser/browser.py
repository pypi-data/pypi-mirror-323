"""Module for managing browser initialization and LinkedIn automation."""

import logging
import os
import subprocess
import sys
from typing import Optional, Tuple

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from .login_page import LoginPage

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


class LinkedInBrowser:
    """Handles browser initialization, management and cleanup for LinkedIn automation.

    This class provides methods to initialize a browser instance, ensure proper setup,
    handle login, and cleanup browser resources when done.
    """

    def __init__(self):
        """Initialize browser-related attributes."""
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def _ensure_browser_install(self):
        """Ensure Playwright browsers are installed."""
        try:
            # Check if PLAYWRIGHT_BROWSERS_PATH is set
            browsers_path = os.getenv("PLAYWRIGHT_BROWSERS_PATH")
            if browsers_path and os.path.exists(browsers_path):
                logger.info(f"Using custom browser path: {browsers_path}")
                return

            # Try to install browsers
            logger.info("Installing Playwright browsers")
            result = subprocess.run(
                ["playwright", "install", "chromium"], capture_output=True, text=True
            )

            if result.returncode != 0:
                logger.warning(f"Browser installation failed: {result.stderr}")
                logger.warning(
                    "Will attempt to proceed anyway as browsers might be installed"
                )
            else:
                logger.info("Browser installation successful")

        except Exception as e:
            logger.warning(f"Error during browser installation: {str(e)}")
            logger.warning("Will attempt to proceed with browser launch")

    async def _ensure_browser(self) -> bool:
        """Ensure browser is initialized with persistent context."""
        # Close any existing sessions
        await self.cleanup()

        try:
            # Ensure browsers are installed
            await self._ensure_browser_install()

            logger.info("Starting Playwright")
            self.playwright = await async_playwright().start()

            # Define user data directory for persistent context
            user_data_dir = os.path.join(
                os.path.expanduser("~"), ".linkedin-automation"
            )

            logger.info("Launching browser with persistent context")
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                viewport={"width": 1280, "height": 720},
                accept_downloads=True,
                ignore_https_errors=True,
                bypass_csp=True,
                slow_mo=100,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            )

            logger.info("Creating new page")
            self.page = await self.context.new_page()

            logger.info("Browser session initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            return False

    async def cleanup(self):
        """Clean up browser context, browser, and Playwright instance."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        finally:
            # Reset all browser-related instances after cleanup
            self.playwright = None
            self.browser = None
            self.context = None
            self.page = None

    async def ensure_browser_and_login(
        self, email: str, password: str, use_profile: bool = True
    ) -> Tuple[Page, bool]:
        """Initialize browser and ensure user is logged in.

        Args:
            email: LinkedIn login email
            password: LinkedIn login password
            use_profile: Whether to attempt using existing profile first

        Returns:
            Tuple of (Page object, success boolean)
        """
        try:
            success = await self._ensure_browser()
            if not success:
                raise Exception("Failed to initialize browser")

            login_page = LoginPage(self.page, use_profile=use_profile)
            await login_page.login(email, password)

            return self.page, True
        except Exception as e:
            logger.error(f"Failed to initialize browser and login: {str(e)}")
            await self.cleanup()
            raise
