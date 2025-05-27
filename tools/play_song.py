import webbrowser
import time
from auth import get_token
import spotipy


def get_track_info(sp, track_id=None):
    """
    Get track information from a provided track ID or URI

    Args:
        sp: Spotify client
        track_id: Track ID or URI

    Returns:
        dict: Track information or None if not found
    """
    # Check if it's a full URI or just an ID
    if track_id.startswith("spotify:track:"):
        track_uri = track_id
        track_id = track_id.split(":")[-1]
    else:
        track_uri = f"spotify:track:{track_id}"

    # Get track info from the ID
    try:
        track = sp.track(track_id)
        return {
            "id": track_id,
            "uri": track_uri,
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "url": track["external_urls"]["spotify"],
        }
    except Exception as e:
        return None


def play_song(track_id):
    """
    Play a specific song on an available Spotify device or open in browser as fallback

    Args:
        track_id (str): Spotify track ID or URI

    Returns:
        dict: Dictionary containing success status, message, and track info
    """
    try:
        # Get authentication token
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Get track information
        track_info = get_track_info(sp, track_id)

        if not track_info:
            return {
                "success": False,
                "message": f"Track with ID '{track_id}' not found",
                "track_info": None,
                "played_on": None,
            }

        # Get available devices
        devices = sp.devices()

        if not devices["devices"]:
            # Open in browser as fallback
            webbrowser.open(track_info["url"])
            return {
                "success": True,
                "message": f"No active Spotify devices found. Opened '{track_info['name']}' by {track_info['artist']} in browser",
                "track_info": track_info,
                "played_on": "browser",
            }

        # Use the first available device
        device_id = devices["devices"][0]["id"]
        device_name = devices["devices"][0]["name"]

        # Start playback on the device
        sp.start_playback(device_id=device_id, uris=[track_info["uri"]])

        # Wait a moment to ensure playback has started
        time.sleep(1)

        # Get current playback to confirm
        playback = sp.current_playback()
        if playback and playback.get("is_playing"):
            return {
                "success": True,
                "message": f"Now playing '{track_info['name']}' by {track_info['artist']} on {device_name}",
                "track_info": track_info,
                "played_on": device_name,
            }
        else:
            # Fallback to browser if playback confirmation fails
            webbrowser.open(track_info["url"])
            return {
                "success": True,
                "message": f"Could not confirm playback. Opened '{track_info['name']}' by {track_info['artist']} in browser",
                "track_info": track_info,
                "played_on": "browser",
            }

    except spotipy.exceptions.SpotifyException as e:
        if "NO_ACTIVE_DEVICE" in str(e):
            # Fallback to browser
            webbrowser.open(track_info["url"])
            return {
                "success": True,
                "message": f"No active Spotify devices found. Opened '{track_info['name']}' by {track_info['artist']} in browser",
                "track_info": track_info,
                "played_on": "browser",
            }
        else:
            return {
                "success": False,
                "message": f"Spotify error: {str(e)}",
                "track_info": track_info if "track_info" in locals() else None,
                "played_on": None,
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error playing song: {str(e)}",
            "track_info": track_info if "track_info" in locals() else None,
            "played_on": None,
        }
