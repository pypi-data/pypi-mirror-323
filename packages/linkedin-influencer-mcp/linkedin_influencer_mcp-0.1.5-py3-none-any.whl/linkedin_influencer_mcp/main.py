# demo.py

"""Module providing high-level LinkedIn automation tools and functionality."""

import logging
import os
from typing import Any, Dict, List, Union

from dotenv import load_dotenv
from fastmcp import FastMCP

from .browser.browser import LinkedInBrowser
from .browser.feed_page import FeedPage
from .browser.profile_page import ProfilePage
from .browser.recent_activity_page import RecentActivityPage
from .browser.search_page.search_page import SearchPage
from .browser.utils import dependencies
from .models import ConnectionRequest, ConnectionRequestResult, ProfileInfo

# Constants
load_dotenv()
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "false"
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
USER_LINKEDIN_PROFILE_ID = os.getenv("USER_LINKEDIN_PROFILE_ID")
if not all([LINKEDIN_EMAIL, LINKEDIN_PASSWORD, GROQ_API_KEY, USER_LINKEDIN_PROFILE_ID]):
    raise ValueError("LinkedIn credentials not found in environment variables")

# Initialize logging
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "LinkedIn Scraper",
    dependencies=dependencies.dependencies,
)


def main():
    """Entry point for the LinkedIn Influencer MCP CLI."""
    mcp.run()


@mcp.tool()
async def get_linkedin_profile_info(
    linkedin_profile_id: str = USER_LINKEDIN_PROFILE_ID,
) -> ProfileInfo:
    """
    Get basic information from a LinkedIn profile.

    Args:
        linkedin_profile_id: LinkedIn profile ID to scrape, use default if not specified

    Returns:
        Dictionary containing profile information (name, headline, location, about)
    """
    browser = None
    try:
        browser = LinkedInBrowser()
        page, _ = await browser.ensure_browser_and_login(
            LINKEDIN_EMAIL, LINKEDIN_PASSWORD
        )

        profile_page = ProfilePage(page)
        return await profile_page.get_profile_info(
            linkedin_profile_id=linkedin_profile_id
        )
    except Exception as e:
        logger.error(f"Failed to get profile info: {str(e)}")
        raise
    finally:
        if browser:
            await browser.cleanup()


@mcp.tool()
async def get_linkedin_profile_posts(
    linkedin_profile_id: Union[str, List[str]], max_posts: int = 5
) -> List[Dict[str, Any]]:
    """
    Get/scrape posts from LinkedIn profiles.

    Args:
        linkedin_profile_id: Single LinkedIn profile ID or list of profile IDs to scrape
        max_posts: Maximum number of posts to scrape per profile

    Returns:
        List of dictionaries containing post information
    """
    browser = None
    try:
        browser = LinkedInBrowser()
        page, _ = await browser.ensure_browser_and_login(
            LINKEDIN_EMAIL, LINKEDIN_PASSWORD
        )

        recent_activity_page = RecentActivityPage(page)
        return await recent_activity_page.scrape_linkedin_posts(
            linkedin_profile_id, max_posts
        )
    except Exception as e:
        logger.error(f"Failed to get profile posts: {str(e)}")
        raise
    finally:
        if browser:
            await browser.cleanup()


@mcp.tool()
async def create_linkedin_post(content: str) -> bool:
    """
    Create a new post on LinkedIn.

    Args:
        content: Text content to post on LinkedIn

    Returns:
        bool: True if post was created successfully
    """
    browser = None
    try:
        browser = LinkedInBrowser()
        page, _ = await browser.ensure_browser_and_login(
            LINKEDIN_EMAIL, LINKEDIN_PASSWORD
        )

        feed_page = FeedPage(page)
        return await feed_page.create_post(content)
    except Exception as e:
        logger.error(f"Failed to create post: {str(e)}")
        raise
    finally:
        if browser:
            await browser.cleanup()


@mcp.tool()
async def send_linkedin_connection_requests(
    connection: ConnectionRequest,
) -> tuple[list[ConnectionRequestResult], dict[str, int]] | list[str]:
    """
    Send connection requests to LinkedIn profiles based on a search query.

    Args:
        connection: Connection request to send to LinkedIn
            connection.search_query: Search terms to find profiles
            connection.max_connections: Maximum number of connection requests to send (default: 3)
            connection.custom_note: Optional custom note to include with requests.
            connection.user_profile_id: Optional profile ID to get user info for custom note
            connection.location: Optional location to search for profiles in
    Returns:
        List of dictionaries containing connection request results
    """
    browser = None
    try:
        browser = LinkedInBrowser()
        page, _ = await browser.ensure_browser_and_login(
            LINKEDIN_EMAIL, LINKEDIN_PASSWORD
        )

        search_page = SearchPage(page)
        return await search_page.send_connection_requests(
            search_query=connection.search_query,
            max_connections=connection.max_connections,
            custom_note=connection.custom_note,
            user_profile_id=connection.user_profile_id,
            location=connection.location,
        )
    except Exception as e:
        logger.error(f"Failed to send connection requests: {str(e)}")
        raise
    finally:
        if browser:
            await browser.cleanup()


@mcp.prompt()
def connection_requests_to_recruiters_prompt(
    max_connections: int = 10, location: str = "San Francisco, CA"
):
    return f"Send {max_connections} linkedin connection requests to recruiters in {location}, don't send a custom note"


@mcp.prompt()
def connection_requests_with_custom_note(
    search_query: str, max_connections: int = 10, location: str = "San Francisco, CA"
):
    return f"Send {max_connections} linkedin connection requests to {search_query} in {location}, including custom note as well"


@mcp.prompt()
def research_and_create_post(topic):
    return f"Research about {topic} and then Write a linkedin post in my writing style and then post it on my linkedin."


@mcp.prompt()
def scrape_linkedin_posts_and_post_to_linkedin(
    linkedin_profile_ids: Union[str, list[str]], max_posts: int
):
    return f"Scrape {max_posts} posts from these linkedin profiles {linkedin_profile_ids}, re-write them in my writing style and then post to LinkedIn."


@mcp.prompt()
def create_linkedin_post_from_youtube(youtube_video_url: str):
    return f"Get transcript for this youtube video {youtube_video_url}, write a post in my writing style on that topic and then post to LinkedIn."
