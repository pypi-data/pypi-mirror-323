"""Package initialization for linkedin_influencer_mcp module."""

from . import main

get_linkedin_profile_info = main.get_linkedin_profile_info
get_linkedin_profile_posts = main.get_linkedin_profile_posts
create_linkedin_post = main.create_linkedin_post
send_linkedin_connection_requests = main.send_linkedin_connection_requests
connection_requests_to_recruiters_prompt = main.connection_requests_to_recruiters_prompt
connection_requests_with_custom_note = main.connection_requests_with_custom_note
research_and_create_post = main.research_and_create_post
scrape_linkedin_posts_and_post_to_linkedin = (
    main.scrape_linkedin_posts_and_post_to_linkedin
)
create_linkedin_post_from_youtube = main.create_linkedin_post_from_youtube

__version__ = "0.1.0"
