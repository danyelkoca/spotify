import spotipy
import time
from core.logger import SpotifyLogger, log_execution

logger = SpotifyLogger.get_logger()


def get_best_device(sp: spotipy.Spotify):
    """
    Get the best available device based on prioritized device types.
    Prioritizes desktop clients over mobile, and both over web players.

    Args:
        sp (spotipy.Spotify): Authenticated Spotify client

    Returns:
        tuple: (device_id, device_name) of the best device, or (None, None) if no devices available
    """
    try:
        # Get available devices
        devices = sp.devices()
        available_devices = devices.get("devices", [])

        if not available_devices:
            logger.info("No active devices found")
            return None, None

        # Device type priorities (lower number = higher priority)
        device_priority = {
            "Computer": 1,  # Desktop client
            "Smartphone": 2,  # Mobile
            "Tablet": 3,  # Tablet
            "Speaker": 4,  # Smart speakers
            "TV": 5,  # TVs
            "WebPlayer": 10,  # Web Players (lowest priority)
        }

        # Sort devices by priority
        def get_device_priority(device):
            device_type = device.get("type", "Unknown")
            is_web_player = (
                "Web Player" in device.get("name", "") or device_type == "WebPlayer"
            )

            # Extra penalty for web players
            if is_web_player:
                return device_priority.get("WebPlayer", 99)

            return device_priority.get(device_type, 50)

        # Sort devices by priority (lowest number first)
        sorted_devices = sorted(available_devices, key=get_device_priority)

        # Log the device order for debugging
        device_list = ", ".join(
            [f"{d['name']} ({d.get('type', 'Unknown')})" for d in sorted_devices]
        )
        logger.debug(f"Available devices (in priority order): {device_list}")

        # Use the highest priority device
        device_id = sorted_devices[0]["id"]
        device_name = sorted_devices[0]["name"]
        device_type = sorted_devices[0].get("type", "Unknown")
        logger.info(f"Selected device: {device_name} ({device_type}) [ID: {device_id}]")

        return device_id, device_name

    except Exception as e:
        logger.error(f"Error getting best device: {str(e)}")
        return None, None


@log_execution
def ensure_playback(sp: spotipy.Spotify, track_id=None):
    """
    Ensures there's an active playback by attempting recovery strategies.
    First tries to resume currently paused playback, then tries playing most recently played track,
    and finally plays a new track if needed.

    Args:
        sp (spotipy.Spotify): Authenticated Spotify client
        track_id (str, optional): Specific track ID to play if no current playback

    Returns:
        bool: True if playback was successfully started or was already active, False otherwise
        dict: Current playback object from Spotify if successful
    """
    try:
        # Get best device
        device_id, device_name = get_best_device(sp)
        if not device_id:
            logger.warning("No available devices found")
            return False, None

        # Check current playback state
        current_playback = sp.current_playback()

        # If already playing, nothing to do
        if current_playback and current_playback.get("is_playing"):
            logger.info(
                f"Playback already active on {current_playback['device']['name']}"
            )
            return True, current_playback

        # Strategy 1: Resume if we have a paused track
        if current_playback and current_playback.get("item"):
            logger.info("Found paused playback, resuming")
            sp.start_playback(device_id=device_id)
            time.sleep(1)
            current_playback = sp.current_playback()
            if current_playback and current_playback.get("is_playing"):
                logger.info(f"Successfully resumed playback on {device_name}")
                return True, current_playback

        # Strategy 2: Use provided track ID if available
        if track_id:
            # Extract ID from URI if needed
            if track_id.startswith("spotify:track:"):
                track_id = track_id.split(":")[-1]

            logger.info(f"Playing specified track {track_id}")
            sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])
            time.sleep(1)
            current_playback = sp.current_playback()
            if current_playback and current_playback.get("is_playing"):
                logger.info(
                    f"Successfully started playback of provided track on {device_name}"
                )
                return True, current_playback

        # Strategy 3: Try to play recently played track
        try:
            recent_tracks = sp.current_user_recently_played(limit=1)
            if recent_tracks and recent_tracks.get("items"):
                recent_id = recent_tracks["items"][0]["track"]["id"]
                logger.info(f"Playing recently played track {recent_id}")
                sp.start_playback(
                    device_id=device_id, uris=[f"spotify:track:{recent_id}"]
                )
                time.sleep(1)
                current_playback = sp.current_playback()
                if current_playback and current_playback.get("is_playing"):
                    logger.info(
                        f"Successfully started playback of recent track on {device_name}"
                    )
                    return True, current_playback
        except Exception as e:
            logger.warning(f"Error trying to play recently played tracks: {str(e)}")

        # Strategy 4: As a last resort, try to play user's saved tracks
        try:
            saved_tracks = sp.current_user_saved_tracks(limit=1)
            if saved_tracks and saved_tracks.get("items"):
                saved_id = saved_tracks["items"][0]["track"]["id"]
                logger.info(f"Playing a track from user's saved tracks: {saved_id}")
                sp.start_playback(
                    device_id=device_id, uris=[f"spotify:track:{saved_id}"]
                )
                time.sleep(1)
                current_playback = sp.current_playback()
                if current_playback and current_playback.get("is_playing"):
                    logger.info(
                        f"Successfully started playback from saved tracks on {device_name}"
                    )
                    return True, current_playback
        except Exception as e:
            logger.warning(f"Error trying to play saved tracks: {str(e)}")

        logger.error("All playback recovery strategies failed")
        return False, None

    except Exception as e:
        logger.error(f"Error ensuring playback: {str(e)}")
        return False, None
