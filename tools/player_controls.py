from auth import get_token
import spotipy


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
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Get current playback state to check if there's an active device
        current_playback = sp.current_playback()

        if (
            not current_playback
            or not current_playback.get("is_playing", False)
            and action != "resume"
        ):
            return {
                "success": False,
                "message": "No active playback found. Please start playing something first.",
            }

        # Handle the requested action
        if action == "pause":
            sp.pause_playback()
            return {"success": True, "message": "Playback paused"}

        elif action == "resume":
            sp.start_playback()
            return {"success": True, "message": "Playback resumed"}

        elif action == "next":
            sp.next_track()
            return {"success": True, "message": "Skipped to next track"}

        elif action == "previous":
            sp.previous_track()
            return {"success": True, "message": "Returned to previous track"}

        elif action == "shuffle":
            # Toggle shuffle state
            current_state = current_playback.get("shuffle_state", False)
            sp.shuffle(not current_state)
            new_state = "on" if not current_state else "off"
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
            return {"success": True, "message": f"Set repeat mode to {state_desc}"}

        else:
            return {"success": False, "message": f"Unknown action: {action}"}

    except spotipy.exceptions.SpotifyException as e:
        return {"success": False, "message": f"Spotify error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Error controlling playback: {str(e)}"}
