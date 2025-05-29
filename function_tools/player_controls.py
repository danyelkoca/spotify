from core.auth import get_token
import spotipy
import time
from core.logger import log_execution, SpotifyLogger
from function_tools.utils import get_best_device, ensure_playback

logger = SpotifyLogger.get_logger()


@log_execution
def player_controls(action):
    """
    Control Spotify playback (pause, resume, next, previous, shuffle, repeat)

    Args:
        action (str): The action to perform (pause, resume, next, previous, shuffle, repeat)

    Returns:
        dict: Dictionary containing success status and message
    """
    try:
        # Get authentication token
        logger.debug("Getting authentication token")
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Get current playback state to check if there's an active device
        logger.debug("Checking current playback state")
        current_playback = sp.current_playback()

        # Select the best device for operations if needed
        device_id, device_name = get_best_device(sp)

        # If no active playback and the action is not resume, try to revive the playback
        if (
            not current_playback or not current_playback.get("is_playing", False)
        ) and action != "resume":
            logger.warning("No active playback found, attempting to revive playback")

            # Use our centralized recovery function
            playback_restored, current_playback = ensure_playback(sp)

            if not playback_restored:
                logger.warning("Could not restore playback")
                return {
                    "success": False,
                    "message": "No active playback could be restored. Please start playing something first.",
                }

        # Get the best available device for playback operations
        device_id = None
        if action == "resume":
            # Only get a specific device for resume action (others work on current device)
            device_id, device_name = get_best_device(sp)
            if device_id:
                logger.debug(f"Using device {device_name} for playback")

        # Handle the requested action
        logger.debug(f"Executing playback action: {action}")
        if action == "pause":
            sp.pause_playback()
            logger.info("Playback paused")
            return {"success": True, "message": "Playback paused"}

        elif action == "resume":
            sp.start_playback(device_id=device_id if device_id else None)
            logger.info(f"Playback resumed{f' on {device_name}' if device_id else ''}")
            return {
                "success": True,
                "message": f"Playback resumed{f' on {device_name}' if device_id else ''}",
            }

        elif action == "next":
            # Ensure the device is active before trying to skip
            if not current_playback or device_id != current_playback.get(
                "device", {}
            ).get("id"):
                logger.debug(f"Activating device {device_name} before skipping")
                try:
                    # Restart playback on the desired device to make it active
                    # We transfer to the device but don't change what's playing
                    if current_playback:
                        track_id = current_playback.get("item", {}).get("id")
                        if track_id:
                            sp.start_playback(
                                device_id=device_id, uris=[f"spotify:track:{track_id}"]
                            )
                            # Brief pause to let API register
                            time.sleep(0.5)
                except Exception as e:
                    logger.warning(f"Couldn't activate device before skip: {str(e)}")

            # Now skip to next track
            sp.next_track()
            logger.info(f"Skipped to next track on {device_name}")
            return {
                "success": True,
                "message": f"Skipped to next track on {device_name}",
            }

        elif action == "previous":
            # Similar device activation logic for previous
            if not current_playback or device_id != current_playback.get(
                "device", {}
            ).get("id"):
                logger.debug(
                    f"Activating device {device_name} before going to previous track"
                )
                try:
                    if current_playback:
                        current_uri = current_playback.get("item", {}).get("uri")
                        if current_uri:
                            sp.start_playback(device_id=device_id, uris=[current_uri])
                            # Brief pause to let API register
                            time.sleep(0.5)
                except Exception as e:
                    logger.warning(
                        f"Couldn't activate device before previous: {str(e)}"
                    )

            sp.previous_track()
            logger.info(f"Returned to previous track on {device_name}")
            return {
                "success": True,
                "message": f"Returned to previous track on {device_name}",
            }

        elif action == "shuffle":
            # Toggle shuffle state
            current_state = current_playback.get("shuffle_state", False)
            sp.shuffle(not current_state)
            new_state = "on" if not current_state else "off"
            logger.info(f"Shuffle turned {new_state}")
            return {"success": True, "message": f"Shuffle turned {new_state}"}

        elif action == "repeat":
            # Cycle through repeat states: off -> context -> track
            current_state = current_playback.get("repeat_state", "off")
            next_state = {
                "off": "context",  # context = repeat playlist/album
                "context": "track",  # track = repeat single track
                "track": "off",  # off = no repeat
            }.get(current_state, "off")

            sp.repeat(next_state)
            state_desc = {
                "context": "playlist/album repeat",
                "track": "track repeat",
                "off": "repeat off",
            }.get(next_state)
            logger.info(f"Set repeat mode to {state_desc}")
            return {"success": True, "message": f"Set repeat mode to {state_desc}"}

        else:
            logger.error(f"Unknown action requested: {action}")
            return {"success": False, "message": f"Unknown action: {action}"}

    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify error in player_controls: {str(e)}")
        return {"success": False, "message": f"Spotify error: {str(e)}"}
    except Exception as e:
        logger.error(f"Error controlling playback: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Error controlling playback: {str(e)}"}
