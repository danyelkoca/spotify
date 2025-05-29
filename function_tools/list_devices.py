from core.auth import get_token
import spotipy
from core.logger import log_execution, SpotifyLogger

logger = SpotifyLogger.get_logger()


@log_execution
def list_devices():
    """
    List all available Spotify devices with their details.

    Returns:
        dict: Dictionary containing success status, message, and list of devices
    """
    try:
        # Get authentication token
        logger.debug("Getting authentication token")
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Get available devices
        logger.debug("Fetching available devices")
        devices = sp.devices()

        available_devices = devices.get("devices", [])

        if not available_devices:
            logger.info("No active Spotify devices found")
            return {
                "success": True,
                "message": "No active Spotify devices found",
                "devices": [],
            }

        # Format device information
        device_list = []
        for device in available_devices:
            device_info = {
                "id": device["id"],
                "name": device["name"],
                "type": device.get("type", "Unknown"),
                "is_active": device["is_active"],
                "volume_percent": device.get("volume_percent", 0),
            }
            device_list.append(device_info)

        # Sort by active status (active first) then by name
        device_list.sort(key=lambda x: (not x["is_active"], x["name"]))

        logger.info(f"Found {len(device_list)} active Spotify devices")
        return {
            "success": True,
            "message": f"Found {len(device_list)} active Spotify devices",
            "devices": device_list,
        }

    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify error listing devices: {str(e)}")
        return {"success": False, "message": f"Spotify error: {str(e)}", "devices": []}
    except Exception as e:
        logger.error(f"Error listing devices: {str(e)}")
        return {
            "success": False,
            "message": f"Error listing devices: {str(e)}",
            "devices": [],
        }
