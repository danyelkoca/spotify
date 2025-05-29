"""Web search functionality using SerpAPI."""

import os
from typing import Dict, Any, List
from serpapi import GoogleSearch
from dotenv import load_dotenv
from core.logger import log_execution, SpotifyLogger

logger = SpotifyLogger.get_logger()
load_dotenv()


@log_execution
def web_search(query: str) -> Dict[str, Any]:
    """
    Search the web using SerpAPI.

    Args:
        query (str): The search query

    Returns:
        dict: Dictionary containing search results and status
    """
    logger = SpotifyLogger.get_logger()
    logger.debug(f"Entering web_search with query={query}")

    try:
        # Get API key from environment variables
        logger.debug("Getting API key from environment variables")
        api_key = os.getenv("SERPAPI_KEY")
        if not api_key:
            logger.error("SERPAPI_KEY not found in environment variables")
            return {
                "success": False,
                "message": "SERPAPI_KEY not found in environment variables",
                "results": [],
            }

        # Initialize search
        logger.debug(f'Performing web search for query: "{query}"')
        search = GoogleSearch(
            {"q": query, "api_key": api_key, "num": 5}  # Limit to top 5 results
        )

        # Get results
        logger.debug("Fetching search results")
        results = search.get_dict()

        # Extract organic results
        organic_results = results.get("organic_results", [])

        # Format results
        formatted_results = []
        for result in organic_results:
            formatted_results.append(
                {
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", ""),
                    "source": "Google Search",
                }
            )
            logger.debug(f"Found result: {result.get('title', '')}")

        if not formatted_results:
            logger.info(f'No results found for query: "{query}"')
            return {"success": False, "message": "No results found", "results": []}

        logger.info(
            f'Successfully found {len(formatted_results)} results for query: "{query}"'
        )
        return {
            "success": True,
            "message": "Search completed successfully",
            "results": formatted_results,
        }

    except Exception as e:
        logger.error(
            f'Error performing web search for query "{query}": {str(e)}', exc_info=True
        )
        return {
            "success": False,
            "message": f"Error performing web search: {str(e)}",
            "results": [],
        }
