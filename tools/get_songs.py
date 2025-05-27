from typing import Dict, List, Any
from auth import get_token
import spotipy


class SongCache:
    _instance = None
    _cache: Dict[str, List[Dict[str, Any]]] = {
        "liked": None,
        "top_short": None,
        "top_medium": None,
        "top_long": None,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SongCache, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_cached_songs(cls, category: str) -> List[Dict[str, Any]]:
        """Get songs from cache for a given category"""
        return cls._cache.get(category)

    @classmethod
    def set_cached_songs(cls, category: str, songs: List[Dict[str, Any]]) -> None:
        """Cache songs for a given category"""
        cls._cache[category] = songs

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached songs"""
        cls._cache = {
            "liked": None,
            "top_short": None,
            "top_medium": None,
            "top_long": None,
        }

    @classmethod
    def clear_category_cache(cls, category: str) -> None:
        """Clear cache for a specific category"""
        if category in cls._cache:
            cls._cache[category] = None


def _fetch_liked_songs(sp: spotipy.Spotify, limit: int = 50) -> List[Dict[str, Any]]:
    """Helper to fetch liked/saved tracks with memory-efficient pagination"""
    try:
        liked_songs = []
        offset = 0
        batch_size = min(20, limit)  # Smaller batch size for better memory usage

        # Get total count first with a minimal request
        initial_results = sp.current_user_saved_tracks(limit=1)
        total = min(initial_results["total"], limit)

        while offset < total:
            results = sp.current_user_saved_tracks(limit=batch_size, offset=offset)
            if not results["items"]:
                break

            # Process songs in batches
            batch_songs = [
                {
                    "name": item["track"]["name"],
                    "artist": item["track"]["artists"][0]["name"],
                    "id": item["track"]["id"],
                    "uri": item["track"]["uri"],
                    "album": item["track"]["album"]["name"],
                    "popularity": item["track"]["popularity"],
                    "duration_ms": item["track"]["duration_ms"],
                    "url": item["track"]["external_urls"]["spotify"],
                    "added_at": item["added_at"],
                    "source": "liked",
                }
                for item in results["items"]
            ]

            liked_songs.extend(batch_songs)
            offset += len(batch_songs)

            # Break early if we've reached the limit
            if len(liked_songs) >= limit:
                liked_songs = liked_songs[:limit]
                break

        return liked_songs
    except Exception as e:
        print(f"Error fetching liked songs: {str(e)}")
        return []


def _fetch_top_songs(
    sp: spotipy.Spotify, time_range: str, limit: int = 50
) -> List[Dict[str, Any]]:
    """Helper to fetch top tracks for a specific time range"""
    try:
        batch_size = min(20, limit)  # Smaller batch size for better memory usage
        results = sp.current_user_top_tracks(time_range=time_range, limit=batch_size)

        if not results["items"]:
            return []

        return [
            {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "id": track["id"],
                "uri": track["uri"],
                "album": track["album"]["name"],
                "popularity": track["popularity"],
                "duration_ms": track["duration_ms"],
                "url": track["external_urls"]["spotify"],
                "source": f"top_{time_range}",
            }
            for track in results["items"][:limit]
        ]
    except Exception as e:
        print(f"Error fetching top songs: {str(e)}")
        return []


def get_songs(limit: int = 50) -> Dict[str, Any]:
    """
    Get user's complete music collection including liked songs and top tracks from all time periods.
    Results are cached for faster subsequent access.

    Args:
        limit (int): Maximum number of songs to return per category (default: 50, max: 50)

    Returns:
        dict: Dictionary containing:
            - success (bool): Operation success status
            - message (str): Status message
            - tracks (List[Dict]): Combined unique tracks from all sources
            - total (int): Total number of unique tracks
            - sources (List[str]): List of sources that contributed tracks
    """
    try:
        cache = SongCache()
        seen_ids = set()  # Track IDs we've seen to avoid duplicates
        unique_songs = []  # Store unique songs
        sources = set()  # Use set for sources to avoid duplicates efficiently

        # Get authentication token
        token_info = get_token()
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Helper function to process songs efficiently
        def process_songs(songs, source):
            if songs:
                sources.add(source)
                for song in songs:
                    if song["id"] not in seen_ids:
                        seen_ids.add(song["id"])
                        unique_songs.append(song)

        # Get liked songs (from cache or API)
        liked_songs = cache.get_cached_songs("liked")
        if liked_songs is None:
            liked_songs = _fetch_liked_songs(sp, limit)
            if liked_songs:
                cache.set_cached_songs("liked", liked_songs)
            else:
                cache.clear_category_cache("liked")
        process_songs(liked_songs, "liked")

        # Get top songs from different time periods
        time_ranges = [
            ("top_short", "short_term"),
            ("top_medium", "medium_term"),
            ("top_long", "long_term"),
        ]

        for cache_key, time_range in time_ranges:
            top_songs = cache.get_cached_songs(cache_key)
            if top_songs is None:
                top_songs = _fetch_top_songs(sp, time_range, limit)
                if top_songs:
                    cache.set_cached_songs(cache_key, top_songs)
            process_songs(top_songs, f"top_{time_range}")

        if not unique_songs:
            return {
                "success": False,
                "message": "No songs found in any category. Please try again.",
                "tracks": [],
                "total": 0,
                "sources": [],
            }

        return {
            "success": True,
            "message": f"Found {len(unique_songs)} unique songs from sources: {', '.join(sorted(sources))}",
            "tracks": unique_songs,
            "total": len(unique_songs),
            "sources": sorted(list(sources)),
        }

    except Exception as e:
        # Clear liked songs cache on error to force refresh next time
        cache = SongCache()
        cache.clear_category_cache("liked")
        print(f"Error in get_songs: {str(e)}")  # Add error logging

        return {
            "success": False,
            "message": f"Error fetching music collection: {str(e)}",
            "tracks": [],
            "total": 0,
            "sources": [],
        }
