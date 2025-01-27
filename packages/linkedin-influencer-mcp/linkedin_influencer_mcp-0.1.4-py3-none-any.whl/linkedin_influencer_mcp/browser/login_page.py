"""Module for handling LinkedIn login functionality."""

import logging
from typing import Optional

from playwright.async_api import Page, TimeoutError

# Constants
SELECTORS = {
    "EMAIL": 'input[id="username"]',
    "PASSWORD": 'input[id="password"]',
    "SUBMIT": 'button[type="submit"]',
}

VALID_REDIRECT_PATHS = ["feed", "checkpoint", "security-verification"]
LOGIN_URL = "https://www.linkedin.com/login"
LOGIN_TIMEOUT = 60000
REDIRECT_TIMEOUT = 30000

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoginPage:
    """Handles LinkedIn login functionality and session management."""

    def __init__(self, page: Page, use_profile: bool = False):
        """Initialize LoginPage with a Playwright page instance.

        Args:
            page: Playwright Page object for browser interaction
            use_profile: Whether to attempt using existing profile first
        """
        self.page = page
        self.use_profile = use_profile
        self._setup_locators()

    def _setup_locators(self):
        """Initialize page locators."""
        self.email_input = self.page.locator(SELECTORS["EMAIL"])
        self.password_input = self.page.locator(SELECTORS["PASSWORD"])
        self.login_button = self.page.locator(SELECTORS["SUBMIT"])

    async def login(
        self, email: Optional[str] = None, password: Optional[str] = None
    ) -> bool:
        """Handle LinkedIn login with proper error handling and logging."""
        try:
            # Try using existing profile first
            if self.use_profile:
                logger.info("Attempting to use existing profile")
                await self.page.goto("https://www.linkedin.com", timeout=LOGIN_TIMEOUT)

                if await self.is_logged_in():
                    logger.info("Successfully logged in using existing profile")
                    return True
                logger.info("No valid session found in profile, proceeding with login")

            # Fallback to regular login if profile login fails or is not enabled
            if not all([email, password]):
                raise ValueError("Email and password must be provided")

            if await self.is_logged_in():
                logger.info("Already logged in, skipping login process")
                return True

            logger.info("Attempting LinkedIn login")
            await self.page.goto(LOGIN_URL, timeout=LOGIN_TIMEOUT)

            await self.email_input.fill(email)
            await self.password_input.fill(password)
            await self.login_button.click()

            try:
                await self.page.wait_for_url(
                    lambda url: any(path in url for path in VALID_REDIRECT_PATHS),
                    timeout=REDIRECT_TIMEOUT,
                )
            except TimeoutError:
                raise Exception("Login failed: Timeout waiting for redirect")

            return self._verify_login_success()

        except Exception as e:
            logger.error(f"Login failed with error: {str(e)}")
            raise

    def _verify_login_success(self) -> bool:
        """Verify login success based on current URL."""
        current_url = self.page.url
        if "feed" in current_url:
            logger.info("Successfully logged in")
            return True
        if any(path in current_url for path in VALID_REDIRECT_PATHS[1:]):
            logger.warning("Security verification required")
            return False
        raise Exception(f"Unexpected redirect URL: {current_url}")

    async def is_logged_in(self) -> bool:
        """Check if user is currently logged in to LinkedIn."""
        try:
            current_url = self.page.url
            return "feed" in current_url or "mynetwork" in current_url
        except Exception as e:
            logger.error(f"Error checking login status: {str(e)}")
            return False
