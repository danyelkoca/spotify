from auth import get_token
import spotipy
from logger import log_execution, SpotifyLogger

logger = SpotifyLogger.get_logger()


@log_execution
def search_songs(query, limit=10):
    """
    Search for songs on Spotify and return essential track information.
    Results are sorted by popularity and relevance.

    Args:
        query (str): Search query for songs
        limit (int): Maximum number of results to return (default: 10)

    Returns:
        dict: Dictionary containing success status, message, and list of tracks
              with essential fields (id, name, artist, album, popularity)
    """
    # Cap limit at 50 (Spotify API maximum)
    limit = min(int(limit), 50)
    try:
        # Get authentication token
        logger.debug("Getting authentication token")
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Search for tracks
        logger.debug(f'Searching for tracks with query: "{query}", limit: {limit}')
        results = sp.search(
            q=query, type="track", limit=20
        )  # Get more results for deduplication

        if not results["tracks"]["items"]:
            logger.info(f'No songs found matching query: "{query}"')
            return {
                "success": False,
                "message": f"No songs found matching '{query}'",
                "tracks": [],
            }

        # Extract only essential track information
        tracks = []
        seen = set()
        for i, track in enumerate(results["tracks"]["items"]):
            # Create a unique key for each song using name and artist
            key = (track["name"].lower(), track["artists"][0]["name"].lower())
            if key not in seen:
                seen.add(key)
                track_info = {
                    "id": track["id"],  # Required for playing the song
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album": track["album"]["name"],
                    "popularity": track["popularity"],
                    # Get genres if available (some tracks might not have this)
                    "genres": track["artists"][0].get("genres", []),
                }
                tracks.append(track_info)
                logger.debug(
                    f"Found track: {track_info['name']} by {track_info['artist']} (popularity: {track_info['popularity']})"
                )
                if len(tracks) >= limit:
                    break

        if not tracks:
            logger.info(f'No tracks found matching "{query}"')
            return {
                "success": False,
                "message": f'No tracks found matching "{query}"',
                "tracks": [],
            }

        # Sort tracks by popularity (highest first)
        tracks.sort(key=lambda x: (-x["popularity"], x["name"]))

        logger.info(f'Found {len(tracks)} tracks matching "{query}"')
        return {
            "success": True,
            "message": f"Found {len(tracks)} tracks matching '{query}'",
            "tracks": tracks,
        }

    except Exception as e:
        logger.error(
            f'Error searching for songs with query "{query}": {str(e)}', exc_info=True
        )
        return {
            "success": False,
            "message": f"Error searching for songs: {str(e)}",
            "tracks": [],
        }
