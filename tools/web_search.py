"""Web search functionality using SerpAPI."""

import os
from typing import Dict, Any, List
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()


def web_search(query: str) -> Dict[str, Any]:
    """
    Search the web using SerpAPI.

    Args:
        query (str): The search query

    Returns:
        dict: Dictionary containing search results and status
    """
    try:
        # Get API key from environment variables
        api_key = os.getenv("SERPAPI_KEY")
        if not api_key:
            return {
                "success": False,
                "message": "SERPAPI_KEY not found in environment variables",
                "results": [],
            }

        # Initialize search
        search = GoogleSearch(
            {"q": query, "api_key": api_key, "num": 5}  # Limit to top 5 results
        )

        # Get results
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

        if not formatted_results:
            return {"success": False, "message": "No results found", "results": []}

        return {
            "success": True,
            "message": "Search completed successfully",
            "results": formatted_results,
        }

    except Exception as e:
        print(f"Error performing web search: {str(e)}")
        return {
            "success": False,
            "message": f"Error performing web search: {str(e)}",
            "results": [],
        }
