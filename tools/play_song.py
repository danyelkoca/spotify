import webbrowser
from auth import get_token
import spotipy
from logger import log_execution, SpotifyLogger
from tools.utils import get_best_device

logger = SpotifyLogger.get_logger()


@log_execution
def get_track_info(sp, track_id=None):
    """
    Get track information from a provided track ID

    Args:
        sp: Spotify client
        track_id: Track ID

    Returns:
        dict: Track information or None if not found
    """
    try:
        # Extract ID from URI if someone passes a URI
        if track_id and track_id.startswith("spotify:track:"):
            track_id = track_id.split(":")[-1]

        logger.debug(f"Fetching track info for ID: {track_id}")
        track = sp.track(track_id)
        track_info = {
            "id": track_id,
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "url": track["external_urls"]["spotify"],
        }
        logger.info(
            f"Successfully retrieved track info for '{track_info['name']}' by {track_info['artist']}"
        )
        return track_info
    except Exception as e:
        logger.error(f"Failed to get track info for ID {track_id}: {str(e)}")
        return None


@log_execution
def play_song(track_id):
    """
    Play a specific song on an available Spotify device or open in browser as fallback

    Args:
        track_id (str): Spotify track ID

    Returns:
        dict: Dictionary containing success status and message
    """
    try:
        # Get authentication token
        logger.debug("Getting authentication token")
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Extract ID from URI if someone passes a URI
        if track_id and track_id.startswith("spotify:track:"):
            track_id = track_id.split(":")[-1]

        # Get track information
        logger.debug(f"Getting track information for ID: {track_id}")
        track_info = get_track_info(sp, track_id)

        if not track_info:
            logger.warning(f"Track with ID '{track_id}' not found")
            return {
                "success": False,
                "message": f"Track with ID '{track_id}' not found",
            }

        # Get the best available device using our utility function
        logger.debug("Finding best available device")
        device_id, device_name = get_best_device(sp)

        if not device_id:
            logger.info(
                f"No active devices found, opening '{track_info['name']}' in browser"
            )
            webbrowser.open(track_info["url"])
            return {
                "success": True,
                "message": f"No active Spotify devices found. Opened '{track_info['name']}' by {track_info['artist']} in browser",
            }

        # Start playback on the device
        logger.debug(f"Starting playback of '{track_info['name']}' on {device_name}")
        try:
            sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])
            logger.info(f"Successfully playing '{track_info['name']}' on {device_name}")
            return {
                "success": True,
                "message": f"Now playing '{track_info['name']}' by {track_info['artist']} on {device_name}",
            }
        except spotipy.exceptions.SpotifyException as e:
            if "NO_ACTIVE_DEVICE" in str(e):
                logger.warning(
                    f"No active device available, opening '{track_info['name']}' in browser"
                )
                webbrowser.open(track_info["url"])
                return {
                    "success": True,
                    "message": f"No active Spotify devices found. Opened '{track_info['name']}' by {track_info['artist']} in browser",
                }
            else:
                raise

    except spotipy.exceptions.SpotifyException as e:
        logger.error(
            f"Spotify error while playing '{track_info['name'] if 'track_info' in locals() else track_id}': {str(e)}"
        )
        return {
            "success": False,
            "message": f"Spotify error: {str(e)}",
        }
    except Exception as e:
        logger.error(
            f"Unexpected error while playing '{track_info['name'] if 'track_info' in locals() else track_id}': {str(e)}"
        )
        return {
            "success": False,
            "message": f"Error playing song: {str(e)}",
        }
