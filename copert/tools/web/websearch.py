"""Web search tool using Exa API."""

from typing import Optional, List
from langchain_core.tools import tool
from exa_py import Exa
from copert.config import settings


@tool(parse_docstring=True)
def websearch(query: str, allowed_domains: Optional[List[str]] = None, blocked_domains: Optional[List[str]] = None) -> str:
    """Search the web using Exa API and return results.

    This tool:
    - Allows Claude to search the web and use the results to inform responses
    - Provides up-to-date information for current events and recent data
    - Returns search result information formatted as search result blocks
    - Use this tool for accessing information beyond Claude's knowledge cutoff
    - Searches are performed automatically within a single API call

    Usage notes:
    - Domain filtering is supported to include or block specific websites
    - The query should be clear and specific (minimum 2 characters)

    Args:
        query: The search query to use (minimum 2 characters)
        allowed_domains: Only include search results from these domains (optional)
        blocked_domains: Never include search results from these domains (optional)

    Returns:
        Formatted search results with titles, URLs, and snippets, or error message
    """
    try:
        # Validate query
        if not query or len(query) < 2:
            return "Error: Query must be at least 2 characters long"

        # Initialize Exa client
        try:
            exa = Exa(api_key=settings.exa_api_key)
        except Exception as e:
            return f"Error initializing Exa client. Make sure EXA_API_KEY is set in .env: {str(e)}"

        # Prepare search parameters
        search_params = {
            "query": query,
            "num_results": 10,
            "use_autoprompt": True,  # Let Exa optimize the query
        }

        # Add domain filters if provided
        if allowed_domains:
            search_params["include_domains"] = allowed_domains

        if blocked_domains:
            search_params["exclude_domains"] = blocked_domains

        # Perform search with contents
        try:
            # Use search_and_contents to get both results and text snippets
            response = exa.search_and_contents(
                **search_params,
                text={"max_characters": 500}  # Get text snippets
            )
        except Exception as e:
            return f"Error performing search: {str(e)}"

        # Check if we got results
        if not response or not response.results or len(response.results) == 0:
            return f"No results found for query: {query}"

        # Format results
        output = f"Search Results for: {query}\n"
        output += "=" * 80 + "\n\n"

        for i, result in enumerate(response.results, 1):
            output += f"{i}. {result.title}\n"
            output += f"   URL: {result.url}\n"

            # Add text snippet if available
            if hasattr(result, 'text') and result.text:
                # Truncate long snippets
                snippet = result.text.strip()
                if len(snippet) > 300:
                    snippet = snippet[:300] + "..."
                output += f"   {snippet}\n"

            # Add published date if available
            if hasattr(result, 'published_date') and result.published_date:
                output += f"   Published: {result.published_date}\n"

            # Add author if available
            if hasattr(result, 'author') and result.author:
                output += f"   Author: {result.author}\n"

            output += "\n"

        output += f"\nTotal results: {len(response.results)}"

        # Add autoprompt info if available
        if hasattr(response, 'autoprompt_string') and response.autoprompt_string:
            output += f"\n\nOptimized query used: {response.autoprompt_string}"

        return output

    except Exception as e:
        return f"Error in websearch: {str(e)}"
