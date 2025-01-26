<div align="center">

<!-- omit in toc -->
# LinkedIn Influencer MCP 🎯
<strong>A powerful MCP server for automating LinkedIn interactions and content analysis.</strong>

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Diagram
![LinkedIn Influencer MCP Architecture](https://github.com/shahshrey/linkedin_influencer_mcp/blob/main/src/assets/flow.png)

</div>

This Model Context Protocol (MCP) server provides tools and resources for automating LinkedIn interactions, analyzing profiles, and managing content. Built with FastMCP, it enables AI assistants to perform complex LinkedIn operations including profile analysis, content creation, and network building.

## Table of Contents

- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Development](#development)
- [Tools and Prompts](#tools-and-prompts)

## Installation

We recommend installing with [uv](https://docs.astral.sh/uv/):

```bash
# Clone the repository
git clone git@github.com:shahshrey/linkedin_influencer_mcp.git
cd linkedin_influencer_mcp

# Install dependencies
uv sync
```

### Dependencies

Key dependencies include:
- `fastmcp~=0.4.1`: Core MCP functionality
- `langchain_core` & `langchain_community`: LangChain integration
- `playwright~=1.49.1`: Browser automation
- `python-dotenv~=1.0.1`: Environment management
- `beautifulsoup4~=4.12.3`: HTML parsing
- `pydantic~=2.10.6`: Data validation

## Features

- **Profile Analysis**: 
  - Extract comprehensive LinkedIn profile data including name, headline, experience, education
  - Analyze profile strength and engagement metrics
  - Track profile changes over time
  - Generate insights about professional background

- **Content Management**: 
  - Create and schedule LinkedIn posts with optimal timing
  - Scrape and analyze posts from target profiles
  - Track post performance and engagement
  - Generate content from YouTube video transcripts
  - Repurpose content across platforms

- **Network Building**: 
  - Send personalized connection requests at scale
  - Search and connect with specific professional groups
  - Automated recruiter outreach with customized messaging
  - Track connection request status and responses
  - Build targeted professional networks

- **Content Generation**:
  - AI-powered post creation using multiple LLM options
  - Content repurposing from various sources (YouTube, articles, etc.)
  - Writing style mimicking based on successful profiles
  - SEO optimization for maximum visibility
  - Hashtag optimization and trend analysis

- **Automation Tools**:
  - Headless browser automation with Playwright
  - Robust session management and cookie handling
  - Rate limiting protection
  - Comprehensive error handling and recovery
  - Detailed logging and monitoring

## Usage

1. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials:
LINKEDIN_EMAIL=your-email
LINKEDIN_PASSWORD=your-password
GROQ_API_KEY=your-groq-api-key
USER_LINKEDIN_PROFILE_ID=your-profile-id
```

2. Run the MCP server:
```bash
fastmcp install linkedin_influencer.py
```

3. Available Tools:
```python
# Get profile information
await get_linkedin_profile_info(linkedin_profile_id="profile_id")

# Scrape posts
await get_linkedin_profile_posts(linkedin_profile_id="profile_id", max_posts=5)

# Create a post
await create_linkedin_post(content="Your post content")

# Send connection requests
await send_linkedin_connection_requests(connection=ConnectionRequest(...))
```

## Configuration

Required environment variables:

- `LINKEDIN_EMAIL`: Your LinkedIn account email
- `LINKEDIN_PASSWORD`: Your LinkedIn password
- `GROQ_API_KEY`: Groq API key for AI operations
- `USER_LINKEDIN_PROFILE_ID`: Your LinkedIn profile ID
- `GOOGLE_API_KEY`: If you prefer to use Gemini
- `OPENAI_API_KEY`: If you prefer to use OpenAI
- `LANGCHAIN_API_KEY`: For LangSmith tracking operations
- `LANGCHAIN_PROJECT`: LangChain project name
- `LANGCHAIN_TRACING_V2`: Enable LangChain tracing

## Project Structure

```
linkedin_influencer_mcp/
├── src/                    # Source code
│   ├── browser/           # Browser automation
│   │   ├── feed_page.py
│   │   ├── profile_page.py
│   │   └── search_page.py
├── tests/                 # Test suite
├── linkedin_influencer.py # Main MCP server
├── requirements.txt       # Dependencies
├── pyproject.toml        # Project configuration
└── .env                  # Environment variables
```

## Development

### Prerequisites

- Python 3.10+
- uv package manager
- LinkedIn account
- Required API keys (see below)

### Getting Your API Keys

#### 1. Groq API Key
1. Visit [Groq Cloud](https://console.groq.com)
2. Sign up for an account
3. Navigate to API Keys section
4. Generate a new API key

#### 2. Google API Key (Optional - for Gemini)
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Create a project
3. Enable the Gemini API
4. Generate API credentials

#### 3. OpenAI API Key (Optional)
1. Visit [OpenAI Platform](https://platform.openai.com)
2. Sign up/Login
3. Navigate to API section
4. Create a new API key

Note on API Usage:
- Groq: Pay-as-you-go pricing
- Google: Free tier available with quotas
- OpenAI: Usage-based pricing

Choose APIs based on your needs and budget. Groq is recommended for optimal performance.

### Configure as MCP Server

To add this tool as an MCP server, modify your Claude desktop configuration file:

- MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Add the following configuration:

```json
{
    "linkedin-influencer-mcp": {
        "command": "uv",
        "args": [
            "--directory",
            "/Users/YOUR_USERNAME/path/to/linkedin_influencer_mcp",
            "run",
            "linkedin_influencer"
        ],
        "env": {
            "LINKEDIN_EMAIL": "your_email",
            "LINKEDIN_PASSWORD": "your_password",
            "GROQ_API_KEY": "your_groq_key",
            "USER_LINKEDIN_PROFILE_ID": "your_profile_id"
        }
    }
}
```

Alternatively, you can also give Claude access to the server by running:

```bash
fastmcp install linkedin_influencer.py
```

⚠️ IMPORTANT: 
1. Replace placeholders with your actual credentials
2. Ensure directory path matches your installation
3. Never commit this file with real credentials

### Local Development

1. Install development dependencies:
```bash
uv pip install -r requirements.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest tests/
```

4. Use the MCP Inspector for testing:
```bash
fastmcp dev linkedin_influencer.py
```

### Code Style

The project uses:
- Black for code formatting
- Flake8 for linting
- isort for import sorting
- pre-commit hooks for automated checks

### Debugging

Since MCP servers run over stdio, we recommend using the MCP Inspector for debugging:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/linkedin_influencer_mcp run linkedin_influencer
```

The Inspector provides:
- Real-time request/response monitoring
- Input/output validation
- Error tracking
- Performance metrics

## Tools and Prompts

### Available Tools

- `get_linkedin_profile_info`: Extract profile information
- `get_linkedin_profile_posts`: Scrape posts from profiles
- `create_linkedin_post`: Create and publish posts
- `send_linkedin_connection_requests`: Automated networking

### Prompt Templates

- `connection_requests_to_recruiters_prompt`: Generate personalized outreach messages to recruiters based on job preferences and experience
- `connection_requests_with_custom_note`: Create tailored connection requests with context-aware messaging
- `research_and_create_post`: Leverage Brave/Perplexity MCP for research, then generate content using Claude's writing style for authentic LinkedIn posts and post to linkedin directly from claude
- `scrape_linkedin_posts_and_post_to_linkedin`: Analyze successful content from influencers, extract key themes, and create unique posts
- `create_linkedin_post_from_youtube`: Convert YouTube video content into engaging LinkedIn posts with proper attribution

## Use Cases

### Example #1: Automated Recruiter Outreach

Use the recruiter outreach template to automatically connect with relevant recruiters:

<img width="693" alt="Recruiter Outreach Example" src="https://github.com/user-attachments/assets/PLACEHOLDER_FOR_SCREENSHOT" />

Example prompt to Claude:
```
Connect with tech recruiters in the San Francisco Bay Area who are hiring for senior software engineering roles. Personalize the message based on my experience with Python and distributed systems.
```

### Example #2: Content Creation from Research

Use the research and post creation template to generate engaging content:

Example prompt:
```
Research the latest trends in AI and create a LinkedIn post about the impact of large language models on software development. Include relevant statistics and tag key influencers in the space.
```

## Error Handling

The service includes robust error handling for:
- LinkedIn rate limiting
- Authentication failures
- Network timeouts
- API quota exceeded
- Invalid input parameters
- Session management issues

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
