"""Play songs by name without needing two separate function calls"""

from .search_songs import search_songs
from .play_song import play_song


def play_song_by_name(song_name: str):
    """
    Search for a song by name and play the top result

    Args:
        song_name (str): Name of the song to search for and play

    Returns:
        dict: Dictionary with playback details and song info
    """
    # Clean up the song name and ensure exact search
    # Remove "by" and split artist and title if provided
    song_name = song_name.strip()
    artist = None
    title = song_name

    if " by " in song_name.lower():
        parts = song_name.split(" by ", 1)
        title = parts[0].strip()
        artist = parts[1].strip()

    # First search for the song with exact parameters
    search_query = title
    if artist:
        search_query = f"artist:{artist} track:{title}"

    # Search for the song
    search_result = search_songs(search_query, limit=1)

    # Check if search was successful
    if not search_result.get("success") or not search_result.get("tracks"):
        return {
            "success": False,
            "message": f"Couldn't find the song '{title}'{f' by {artist}' if artist else ''}",
            "track_info": None,
            "played_on": None,
        }

    # Get the top search result
    track = search_result["tracks"][0]
    track_id = track["id"]

    # Play the song
    play_result = play_song(track_id)

    # Add search context to the result
    play_result["search_query"] = song_name

    return play_result
