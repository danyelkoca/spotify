from auth import get_token
import spotipy


def search_songs(query, limit=5):
    """
    Search for songs on Spotify and return detailed information including song IDs

    Args:
        query (str): Search query for songs
        limit (int): Maximum number of results to return

    Returns:
        list: List of songs with their details
    """
    try:
        # Get authentication token
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Search for tracks
        results = sp.search(q=query, type="track", limit=limit)

        if not results["tracks"]["items"]:
            return {
                "success": False,
                "message": f"No songs found matching '{query}'",
                "tracks": [],
            }

        # Extract relevant track information
        tracks = []
        for i, track in enumerate(results["tracks"]["items"]):
            track_info = {
                "id": track["id"],
                "uri": track["uri"],
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "duration_ms": track["duration_ms"],
                "popularity": track["popularity"],
                "url": track["external_urls"]["spotify"],
            }
            tracks.append(track_info)

        return {
            "success": True,
            "message": f"Found {len(tracks)} tracks matching '{query}'",
            "tracks": tracks,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error searching for songs: {str(e)}",
            "tracks": [],
        }
