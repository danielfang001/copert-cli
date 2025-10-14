"""Web content fetching tool."""

import requests
from bs4 import BeautifulSoup
import html2text
from typing import Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from copert.config import settings


# Simple in-memory cache with 15-minute TTL
_cache = {}
_CACHE_TTL = timedelta(minutes=15)


def _clean_cache():
    """Remove expired cache entries."""
    global _cache
    now = datetime.now()
    expired_keys = [k for k, (_, timestamp) in _cache.items() if now - timestamp > _CACHE_TTL]
    for key in expired_keys:
        del _cache[key]


@tool(parse_docstring=True)
def webfetch(url: str, prompt: str) -> str:
    """Fetch content from a specified URL and process it using an AI model.

    This tool:
    - Takes a URL and a prompt as input
    - Fetches the URL content, converts HTML to markdown
    - Processes the content with the prompt using a small, fast model
    - Returns the model's response about the content
    - Use this tool when you need to retrieve and analyze web content

    Usage notes:
    - The URL must be a fully-formed valid URL
    - HTTP URLs will be automatically upgraded to HTTPS
    - The prompt should describe what information you want to extract from the page
    - This tool is read-only and does not modify any files
    - Results may be summarized if the content is very large
    - Includes a self-cleaning 15-minute cache for faster responses when repeatedly accessing the same URL
    - When a URL redirects to a different host, the tool will inform you and provide the redirect URL

    Args:
        url: The URL to fetch content from (must be a valid URL)
        prompt: The prompt to run on the fetched content (what information to extract)

    Returns:
        The AI model's response about the content, or error message
    """
    try:
        # Clean expired cache entries
        _clean_cache()

        # Upgrade HTTP to HTTPS
        if url.startswith("http://"):
            url = url.replace("http://", "https://", 1)

        # Validate URL format
        if not url.startswith("https://") and not url.startswith("http://"):
            return f"Error: Invalid URL format. URL must start with http:// or https://. Got: {url}"

        # Check cache
        cache_key = f"{url}:{prompt}"
        if cache_key in _cache:
            content, timestamp = _cache[cache_key]
            if datetime.now() - timestamp <= _CACHE_TTL:
                return f"[Cached] {content}"

        # Fetch the URL
        try:
            response = requests.get(
                url,
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; CopertBot/1.0; +https://github.com/copert/copert-cli)"
                },
                allow_redirects=True
            )
            response.raise_for_status()

            # Check if redirected to different host
            if response.url != url:
                from urllib.parse import urlparse
                original_host = urlparse(url).netloc
                redirect_host = urlparse(response.url).netloc
                if original_host != redirect_host:
                    return f"Redirect detected: URL redirected from {original_host} to {redirect_host}. New URL: {response.url}\n\nPlease make a new WebFetch request with the redirect URL to fetch the content."

        except requests.exceptions.Timeout:
            return f"Error: Request timed out after 30 seconds for URL: {url}"
        except requests.exceptions.ConnectionError:
            return f"Error: Failed to connect to URL: {url}"
        except requests.exceptions.HTTPError as e:
            return f"Error: HTTP error {e.response.status_code} for URL: {url}"
        except requests.exceptions.RequestException as e:
            return f"Error fetching URL: {str(e)}"

        # Convert HTML to markdown
        try:
            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text content
            html_content = str(soup)

            # Convert to markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            h.ignore_emphasis = False
            h.body_width = 0  # Don't wrap text
            markdown_content = h.handle(html_content)

            # Truncate if too large (keep first 50000 chars)
            if len(markdown_content) > 50000:
                markdown_content = markdown_content[:50000] + "\n\n[Content truncated due to length...]"

        except Exception as e:
            return f"Error converting HTML to markdown: {str(e)}"

        # Process with LLM
        try:
            llm = ChatOpenAI(
                model="gpt-4o-mini",  # Use faster, cheaper model for processing
                temperature=0.1,
                api_key=settings.openai_api_key
            )

            # Create the processing prompt
            messages = [
                {"role": "system", "content": "You are a helpful assistant that extracts and summarizes information from web content."},
                {"role": "user", "content": f"Here is the content from {url}:\n\n{markdown_content}\n\nTask: {prompt}"}
            ]

            result = llm.invoke(messages)
            content = result.content

            # Cache the result
            _cache[cache_key] = (content, datetime.now())

            return content

        except Exception as e:
            return f"Error processing content with LLM: {str(e)}"

    except Exception as e:
        return f"Error in webfetch: {str(e)}"
