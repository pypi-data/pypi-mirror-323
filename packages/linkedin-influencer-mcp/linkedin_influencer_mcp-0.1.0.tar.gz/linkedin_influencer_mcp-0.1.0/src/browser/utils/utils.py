"""Module for handling LinkedIn search functionality and profile interactions."""

import logging
import os
from typing import Any, cast

from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from src.models import ProfileInfo

logger = logging.getLogger(__name__)
llm = None


# Initialize LLMs lazily to avoid circular imports and handle missing API keys
def get_llm():
    global llm
    if llm is not None:
        return llm

    try:
        if os.getenv("OPENAI_API_KEY"):
            openai_llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.0,
                max_retries=2,
            )
            google_llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.0,
                max_retries=2,
            )
            groq_llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.0,
                max_retries=2,
            )
            llm = openai_llm.with_fallbacks([google_llm, groq_llm])
        elif os.getenv("GOOGLE_API_KEY"):
            google_llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.0,
                max_retries=2,
            )
            openai_llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.0,
                max_retries=2,
            )
            groq_llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.0,
                max_retries=2,
            )
            llm = google_llm.with_fallbacks([openai_llm, groq_llm])
        elif os.getenv("GROQ_API_KEY"):
            groq_llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.0,
                max_retries=2,
            )
            openai_llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.0,
                max_retries=2,
            )
            google_llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.0,
                max_retries=2,
            )
            llm = groq_llm.with_fallbacks([openai_llm, google_llm])
        else:
            raise ValueError("No API key found for OpenAI, Google, or Groq")
        return llm
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        raise


async def scrape_html_profile_info_using_llm(html_element: Any) -> ProfileInfo:
    llm = get_llm()
    soup = BeautifulSoup(html_element, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    cleaned_html = soup.prettify()
    prompt = f"""Extract the following information from this LinkedIn profile card HTML.
            Return only a JSON object with these fields:
            <json_schema>
            {ProfileInfo.model_json_schema()}
            </json_schema>
            HTML:
            {cleaned_html}
            """
    logger.debug(f"Prompt for profile info: {prompt}")
    response = await llm.with_structured_output(ProfileInfo).ainvoke(prompt)
    logger.debug(f"Response for profile info: {response}")
    return cast(ProfileInfo, response)


async def scrape_string_profile_info_using_llm(user_data: str) -> ProfileInfo:
    llm = get_llm()
    prompt = (
        f"""Extract the following information from this LinkedIn profile """
        f"""Return only a JSON object with these fields:
        <json_schema>
        {ProfileInfo.model_json_schema()}
        </json_schema>

        <HTML CONTENT>
        {user_data}
        </HTML CONTENT>

        include the about section as much as possible. We always need to include the about section and all other information thats provided in the html content.
        """
    )
    logger.debug(f"Prompt for profile info: {prompt}")
    response = await llm.with_structured_output(ProfileInfo).ainvoke(prompt)
    logger.debug(f"Response for profile info: {response}")
    return cast(ProfileInfo, response)


async def get_custom_note(search_query, profile_info, user_info):
    llm = get_llm()
    prompt = f"""
        1. your job is to help the user expand their LinkedIn network by sending connection requests with high acceptance probability.

        <Search Context>
        {search_query}
        </Search Context>

        2. Profile Analysis:
        <User's Background>
        {user_info}
        </User's Background>

        <Recipient's Profile>
        {profile_info}
        </Recipient's Profile>

        3. Connection Strategy:
        - Identify 1-2 relevant commonalities (shared skills, experiences, or mutual connections)
        - Highlight value proposition without being transactional
        - Maintain professional tone with natural language

        5. Requirements:
        - Use simple sentence structures
        - Avoid buzzwords and corporate jargon
        - Max 150 characters
        - No emojis or special characters
        - Must reference actual profile details

        Output ONLY the final connection note text without any formatting or explanations.

        example:
        user query: I want to connect with people working in AI and in Canada, I work in AI as well.
        Hi Name, I see you're also working in AI and working in Canada, I wanted to connect with like minded people.
        I'm also working in this field and would appreciate connecting to learn from your experience."""

    logger.debug(f"Prompt for custom note: {prompt}")
    response = await llm.ainvoke(prompt)
    logger.debug(f"Response for custom note: {response}")
    return response.content
