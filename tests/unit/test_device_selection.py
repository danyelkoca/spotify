import spotipy
from core.auth import get_token
from core.logger import SpotifyLogger
from tools.utils import get_best_device

logger = SpotifyLogger.get_logger()


def test_device_selection():
    """
    Test the device selection logic to ensure desktop clients are prioritized over web players
    """
    try:
        print("Testing device priority selection...")
        # Get auth token
        token_info = get_token()
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Get available devices
        devices = sp.devices()
        print(f"\nTotal devices available: {len(devices.get('devices', []))}")

        # Print all devices in order of raw API response
        print("\nDevices as returned by Spotify API:")
        for i, device in enumerate(devices.get("devices", [])):
            print(
                f"{i+1}. {device['name']} ({device.get('type', 'Unknown')}) - ID: {device['id'][:5]}..."
            )

        # Get best device using our utility
        device_id, device_name = get_best_device(sp)

        # Get device details for logging
        device_info = next(
            (d for d in devices.get("devices", []) if d["id"] == device_id), None
        )
        device_type = device_info.get("type", "Unknown") if device_info else "Unknown"

        print(f"\n✅ Selected device: {device_name} ({device_type})")
        print(f"   Device ID: {device_id[:5]}...")

        # Test play functionality
        print("\nTesting playback on selected device...")

        # Try playing a track on the selected device
        try:
            sp.start_playback(
                device_id=device_id, uris=["spotify:track:4cOdK2wGLETKBW3PvgPWqT"]
            )  # Rick Astley - Never Gonna Give You Up
            print("✅ Playback started successfully!")
        except Exception as e:
            print(f"❌ Playback error: {str(e)}")

    except Exception as e:
        print(f"❌ Error in test: {str(e)}")


if __name__ == "__main__":
    test_device_selection()
