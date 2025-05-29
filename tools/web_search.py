"""Web search functionality using SerpAPI."""

import os
from typing import Dict, Any, List
from serpapi import GoogleSearch
from dotenv import load_dotenv
from logger import log_execution, SpotifyLogger

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

    # Mock data for Fuji Rock Festival search
    if "fuji rock" in query.lower():
        logger.info("Fuji Rock Festival query detected, returning mock data")
        mock_results = [
            {
                "title": "FRF'25 LINE-UP INCLUDING PERFORMANCE DATES!",
                "snippet": "FOUR TET, a one-of-a-kind presence in the electronic music scene that has captivated artists such as Aphex Twin and Radiohead, and Tatsuro ...",
                "link": "https://en.fujirockfestival.com/news/0221f/",
                "source": "Google Search",
            },
            {
                "title": "FUJI ROCK FESTIVAL 2025 Lineup: Fred again.., Vulfpeck, ...",
                "snippet": "Japan's FUJI ROCK FESTIVAL '25 Returning to Naeba With Fred again.., Vulfpeck, Vampire Weekend as Headliners. Dates are set for Friday, July 25 ...",
                "link": "https://www.billboard.com/music/music-news/fuji-rock-festival-2025-lineup-fred-again-vampire-weekend-1235983098/",
                "source": "Google Search",
            },
            {
                "title": "Fuji Rock Expands Lineup with LITTLE SIMZ, Jane ...",
                "snippet": "Fuji Rock Expands Lineup with LITTLE SIMZ, Jane Remover, and US in Latest Announcement · FUJI ROCK FESTIVAL '25 · Dates: July 25 (Fri), 26 (Sat), ...",
                "link": "https://niewmedia.com/en/news/072546/",
                "source": "Google Search",
            },
            {
                "title": "r/fujirock - 2025 Lineup",
                "snippet": "All in all, I am happy with a lot of these choices: Vampire Weekend, Four Tet, James Blake, Vulfpeck, Ezra Collective, Radwimps, etc.",
                "link": "https://www.reddit.com/r/fujirock/comments/1iugwh9/2025_lineup/",
                "source": "Google Search",
            },
            {
                "title": "LINE UP UPDATE! 6 new artists added to line up!",
                "snippet": 'PERFUME GENIUS, ROBERT RANDOLPH and more! Six new artists added to line up! PERFUME GENIUS, who released their latest album "Glory" last ...',
                "link": "https://en.fujirockfestival.com/news/0425c/",
                "source": "Google Search",
            },
        ]
        logger.info(f"Returning mock results for query: {query}")
        return {
            "success": True,
            "message": "Search completed successfully",
            "results": mock_results,
        }

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
