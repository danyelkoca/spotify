from auth import get_token
import spotipy


def get_top_songs(limit=5, time_range="short_term"):
    """
    Get the user's top tracks from Spotify

    Args:
        limit (int): Number of tracks to return
        time_range (str): Time range for top tracks:
                         short_term (4 weeks),
                         medium_term (6 months),
                         long_term (years)

    Returns:
        dict: Dictionary containing success status, message, and top tracks
    """
    try:
        # Get authentication token
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Get user's top tracks
        top_tracks_response = sp.current_user_top_tracks(
            limit=limit, time_range=time_range
        )

        if not top_tracks_response.get("items"):
            return {
                "success": False,
                "message": "No top tracks found for this time period",
                "tracks": [],
            }

        # Extract relevant track information
        tracks = []
        for track in top_tracks_response["items"]:
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

        time_range_desc = {
            "short_term": "last 4 weeks",
            "medium_term": "last 6 months",
            "long_term": "several years",
        }.get(time_range, time_range)

        return {
            "success": True,
            "message": f"Found your top {len(tracks)} tracks from the {time_range_desc}",
            "tracks": tracks,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error retrieving top songs: {str(e)}",
            "tracks": [],
        }
