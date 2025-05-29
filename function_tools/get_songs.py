from typing import Dict, List, Any
from core.auth import get_token
import spotipy
from core.logger import log_execution, SpotifyLogger
import requests

logger = SpotifyLogger.get_logger()


class SongCache:
    _instance = None
    _cache = {"liked": {"songs": None, "total": 0, "last_offset": 0}}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SongCache, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_cached_songs(cls) -> List[Dict[str, Any]]:
        """Get liked songs from cache"""
        return cls._cache["liked"]["songs"]

    @classmethod
    def get_cache_info(cls) -> Dict[str, Any]:
        """Get all cache information including pagination details"""
        return cls._cache["liked"]

    @classmethod
    def set_cached_songs(
        cls, songs: List[Dict[str, Any]], total: int, offset: int
    ) -> None:
        """Cache liked songs with pagination information"""
        cls._cache["liked"]["songs"] = songs
        cls._cache["liked"]["total"] = total
        cls._cache["liked"]["last_offset"] = offset

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached songs"""
        cls._cache["liked"] = {"songs": None, "total": 0, "last_offset": 0}


@log_execution
def _fetch_songs(
    sp: spotipy.Spotify, limit: int = 50, offset: int = 0
) -> Dict[str, Any]:
    """
    Fetch user's saved tracks from Spotify with pagination support

    Args:
        sp: Spotify client
        limit: Maximum number of songs to fetch (default: 50)
        offset: Starting position for fetch (default: 0)

    Returns:
        Dict containing:
        - songs: List of song dictionaries
        - total: Total number of available songs
        - offset: Current offset after fetch
    """
    try:
        songs = []
        batch_size = min(50, limit)  # Use Spotify's max limit of 50
        current_offset = offset

        # Get total count first if starting fresh
        if offset == 0:
            logger.debug("Getting initial saved tracks count")
            initial_results = sp.current_user_saved_tracks(limit=1, market="US")
            total_available = initial_results["total"]
            logger.info(f"Found {total_available} total saved tracks")
        else:
            # Use cached total when extending
            cache = SongCache()
            total_available = cache.get_cached_songs()["total"]

        while len(songs) < limit:
            logger.debug(f"Fetching tracks batch from offset {current_offset}")
            results = sp.current_user_saved_tracks(
                limit=batch_size, offset=current_offset, market="US"
            )

            if not results["items"]:
                break

            # Process tracks - only include essential fields
            batch_songs = [
                {
                    "name": item["track"]["name"],
                    "artist": item["track"]["artists"][0]["name"],
                    "album": item["track"]["album"]["name"],
                    "id": item["track"]["id"],
                }
                for item in results["items"]
            ]

            songs.extend(batch_songs)
            current_offset += len(batch_songs)
            logger.debug(
                f"Fetched {len(batch_songs)} tracks, total so far: {len(songs)}"
            )

            # Stop if we've fetched all available songs
            if current_offset >= total_available:
                break

        logger.info(f"Successfully fetched {len(songs)} saved tracks")
        return {"songs": songs, "total": total_available, "offset": current_offset}

    except Exception as e:
        logger.error(f"Error fetching saved tracks: {str(e)}", exc_info=True)
        return {"songs": [], "total": 0, "offset": offset}


@log_execution
def get_songs(limit: int = 50, extend: bool = False) -> Dict[str, Any]:
    """
    Get liked songs from Spotify with pagination support.

    Args:
        limit (int): Number of songs to fetch (max 50 per request)
        extend (bool): Whether to extend existing results or start fresh

    Returns:
        Dict containing songs and pagination info
    """
    cache = SongCache()
    cache_info = cache.get_cache_info()

    # If not extending and we have cached songs, return them
    if not extend and cache_info["songs"] is not None:
        return {
            "songs": cache_info["songs"],
            "total": cache_info["total"],
            "has_more": cache_info["total"] > len(cache_info["songs"]),
        }

    # Initialize or continue from last offset
    offset = (
        cache_info["last_offset"] if extend and cache_info["songs"] is not None else 0
    )

    try:
        # Get token and create Spotify client
        token_info = get_token()
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Use spotipy client to get tracks
        data = sp.current_user_saved_tracks(
            limit=limit, offset=offset, market="US"
        )  # Extract song information
        new_songs = [
            {
                "name": item["track"]["name"],
                "artist": item["track"]["artists"][0]["name"],
                "album": item["track"]["album"]["name"],
                "id": item["track"]["id"],
            }
            for item in data["items"]
        ]

        # Extend existing songs or create new list
        if extend and cache_info["songs"] is not None:
            combined_songs = cache_info["songs"] + new_songs
        else:
            combined_songs = new_songs

        # Update cache with new data
        cache.set_cached_songs(combined_songs, data["total"], offset + len(new_songs))

        return {
            "songs": combined_songs,
            "total": data["total"],
            "has_more": (offset + len(new_songs)) < data["total"],
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching liked songs: {str(e)}")
        return {"songs": [], "total": 0, "has_more": False, "error": str(e)}
