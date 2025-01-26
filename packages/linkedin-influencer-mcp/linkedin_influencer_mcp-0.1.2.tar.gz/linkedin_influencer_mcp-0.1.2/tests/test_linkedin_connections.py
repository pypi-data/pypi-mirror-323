import asyncio
import logging
import os

import pytest
from dotenv import load_dotenv

from src.linkedin_influencer_mcp import send_linkedin_connection_requests
from src.linkedin_influencer_mcp.models import (
    ConnectionRequest,
    ConnectionRequestResult,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
load_dotenv()
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
TEST_SEARCH_QUERY = "AI Engineer"
TEST_MAX_CONNECTIONS = 2
TEST_CUSTOM_NOTE = False
TEST_USER_PROFILE_ID = "shreyshahh"
TEST_LOCATION = "Toronto, ON"


@pytest.mark.asyncio
async def test_send_linkedin_connection_requests():
    """Test sending LinkedIn connection requests with real browser."""
    logger.info("Starting LinkedIn connection requests test")
    try:
        results: tuple[list[ConnectionRequestResult], dict[str, int]] = (
            await send_linkedin_connection_requests(
                connection=ConnectionRequest(
                    search_query=TEST_SEARCH_QUERY,
                    max_connections=TEST_MAX_CONNECTIONS,
                    custom_note=TEST_CUSTOM_NOTE,
                    user_profile_id=TEST_USER_PROFILE_ID,
                    location=TEST_LOCATION,
                )
            )
        )

        logger.info(f"Received results: {results}")
        # Verify the results structure
        assert isinstance(results, tuple), "Results should be a tuple"
        assert (
            len(results[0]) <= TEST_MAX_CONNECTIONS
        ), "Should not exceed max connections"

    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}", exc_info=True)
        pytest.fail(f"Test failed with exception: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_send_linkedin_connection_requests())
