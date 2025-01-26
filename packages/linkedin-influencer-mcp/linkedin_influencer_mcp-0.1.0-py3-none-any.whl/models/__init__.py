import os
from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel, Field

USER_LINKEDIN_PROFILE_ID = os.getenv("USER_LINKEDIN_PROFILE_ID")


class ProfileInfo(BaseModel):
    """Model for storing LinkedIn profile information from search results."""

    profile_name: str = Field(description="Full name of the profile.", default="")
    profile_headline: str = Field(
        description="Job title or headline of the profile.", default=""
    )
    profile_location: str = Field(description="Location of the profile.", default="")
    profile_url: str = Field(description="URL of the profile.", default="")
    profile_id: str = Field(description="ID of the profile.", default="")
    profile_about: str = Field(
        description="About the profile. should be as much as possible description of the person in profile and about section based on all the information available",
        default="",
    )


@dataclass
class ConnectionRequestResult:
    """Represents the result of a connection request attempt."""

    status: str
    profile: ProfileInfo
    note_sent: str


@dataclass
class ProcessResult:
    """Result of processing connect buttons."""

    results: List[ConnectionRequestResult]
    processed_count: int


class ConnectionRequest(BaseModel):
    search_query: str = Field(
        description="Search query to search for people, this represents who to search for"
    )
    max_connections: int = Field(description="Maximum number of connections to allow")
    custom_note: Optional[bool] = Field(
        description="whether to send a custom note or not", default=False
    )
    user_profile_id: Optional[str] = Field(
        description="LinkedIn profile ID to scrape", default=USER_LINKEDIN_PROFILE_ID
    )
    location: Optional[str] = Field(
        description="Search location, to search for people, this represents where to search",
        default="San Francisco, CA",
    )
