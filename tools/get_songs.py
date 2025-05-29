from typing import Dict, List, Any
from auth import get_token
import spotipy
from logger import log_execution, SpotifyLogger

logger = SpotifyLogger.get_logger()


class SongCache:
    _instance = None
    _cache: Dict[str, List[Dict[str, Any]]] = {
        "liked": None,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SongCache, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_cached_songs(cls) -> List[Dict[str, Any]]:
        """Get liked songs from cache"""
        return cls._cache["liked"]

    @classmethod
    def set_cached_songs(cls, songs: List[Dict[str, Any]]) -> None:
        """Cache liked songs"""
        cls._cache["liked"] = songs

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached songs"""
        cls._cache["liked"] = None


@log_execution
def _fetch_songs(sp: spotipy.Spotify, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch user's saved tracks from Spotify

    Args:
        sp: Spotify client
        limit: Maximum number of songs to fetch (default: 50)

    Returns:
        List of song dictionaries with essential fields
    """
    try:
        songs = []
        offset = 0
        batch_size = min(50, limit)  # Use Spotify's max limit of 50

        # Get total count first
        logger.debug("Getting initial saved tracks count")
        initial_results = sp.current_user_saved_tracks(limit=1, market="US")
        total = min(initial_results["total"], limit)
        logger.info(f"Found {total} saved tracks to fetch")

        while offset < total:
            logger.debug(f"Fetching tracks batch from offset {offset}")
            results = sp.current_user_saved_tracks(
                limit=batch_size, offset=offset, market="US"
            )

            if not results["items"]:
                break

            # Process tracks - only include essential fields
            batch_songs = [
                {
                    "name": item["track"]["name"],
                    "artist": item["track"]["artists"][0]["name"],
                    "id": item["track"]["id"],
                }
                for item in results["items"]
            ]

            songs.extend(batch_songs)
            offset += len(batch_songs)
            logger.debug(
                f"Fetched {len(batch_songs)} tracks, total so far: {len(songs)}"
            )

            if len(songs) >= limit:
                songs = songs[:limit]
                break

        logger.info(f"Successfully fetched {len(songs)} saved tracks")
        return songs

    except Exception as e:
        logger.error(f"Error fetching saved tracks: {str(e)}", exc_info=True)
        return []


@log_execution
def get_songs(limit: int = 50) -> Dict[str, Any]:
    """
    Get user's saved tracks (liked songs) from Spotify.
    Results are cached for faster subsequent access.

    Args:
        limit: Maximum number of songs to return (default: 50)

    Returns:
        Dictionary containing:
        - success (bool): Operation success status
        - message (str): Status message
        - tracks (List[Dict]): List of tracks
        - total (int): Total number of tracks
    """
    try:
        cache = SongCache()

        # Check cache first
        logger.debug("Checking cache for saved tracks")
        songs = cache.get_cached_songs()

        if songs is None:
            logger.info("Cache miss, fetching from Spotify API")
            # Get authentication token
            token_info = get_token()
            sp = spotipy.Spotify(auth=token_info["access_token"])

            # Fetch songs from Spotify
            songs = _fetch_songs(sp, limit)

            if songs:
                logger.debug("Caching fetched tracks")
                cache.set_cached_songs(songs)
            else:
                logger.warning("No tracks fetched, clearing cache")
                cache.clear_cache()
        else:
            logger.info(f"Cache hit, found {len(songs)} tracks")

        if not songs:
            return {
                "success": False,
                "message": "No saved tracks found. Try saving some songs on Spotify!",
                "tracks": [],
                "total": 0,
            }

        return {
            "success": True,
            "message": f"Found {len(songs)} saved tracks",
            "tracks": songs,
            "total": len(songs),
        }

    except Exception as e:
        logger.error(f"Error in get_songs: {str(e)}", exc_info=True)
        cache.clear_cache()

        return {
            "success": False,
            "message": f"Error fetching saved tracks: {str(e)}",
            "tracks": [],
            "total": 0,
        }
