import spotipy
from auth import get_token
from logger import SpotifyLogger
from tools.utils import get_best_device
from tools.player_controls import player_controls
from tools.play_song import play_song, get_track_info
import time

logger = SpotifyLogger.get_logger()


def test_player_flow():
    """
    Test the full playback control flow to ensure commands like 'next' work correctly after playing a song
    """
    try:
        print("\n===== Testing Player Controls Flow =====")
        # Get auth token
        token_info = get_token()
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Get best device
        device_id, device_name = get_best_device(sp)
        if not device_id:
            print("❌ No devices available for testing")
            return

        print(f"🔈 Using device: {device_name}")

        # Play first track (Never Gonna Give You Up)
        track_id = "4cOdK2wGLETKBW3PvgPWqT"
        track_info = get_track_info(sp, track_id)
        print(
            f"\n1. Playing first track: {track_info['name']} by {track_info['artist']}"
        )

        result = play_song(track_id)
        if result["success"]:
            print(f"✅ Successfully started playing: {result['message']}")
        else:
            print(f"❌ Failed to start playback: {result['message']}")
            return

        # Wait for track to play a bit
        print("\nWaiting 5 seconds for track to play...")
        time.sleep(5)

        # Check current playback
        current = sp.current_playback()
        if current and current.get("is_playing"):
            print(f"✅ Confirmed track is playing: {current['item']['name']}")
        else:
            print("❌ Playback check failed - track may have stopped")

        # Test next track
        print("\n2. Testing 'next' command...")
        next_result = player_controls("next")
        if next_result["success"]:
            print(f"✅ Next track command succeeded: {next_result['message']}")
        else:
            print(f"❌ Next track command failed: {next_result['message']}")

        # Wait and check what's playing now
        print("\nWaiting 3 seconds to verify next track...")
        time.sleep(3)

        # Try to resume if no active playback
        current = sp.current_playback()
        if not current or not current.get("is_playing"):
            print("Track not playing after 'next', attempting to resume playback...")
            device_id, device_name = get_best_device(sp)
            try:
                sp.start_playback(device_id=device_id)
                time.sleep(1)
                current = sp.current_playback()
            except Exception as e:
                print(f"Error resuming playback: {str(e)}")

        if current and current.get("is_playing"):
            print(
                f"✅ Now playing: {current['item']['name']} by {current['item']['artists'][0]['name']}"
            )
        else:
            print("❌ No active playback after 'next' command")

        # Test previous track
        print("\n3. Testing 'previous' command...")
        prev_result = player_controls("previous")
        if prev_result["success"]:
            print(f"✅ Previous track command succeeded: {prev_result['message']}")
        else:
            print(f"❌ Previous track command failed: {prev_result['message']}")

        # Wait and check what's playing now
        print("\nWaiting 3 seconds to verify previous track...")
        time.sleep(3)

        current = sp.current_playback()
        if current and current.get("is_playing"):
            print(
                f"✅ Now playing: {current['item']['name']} by {current['item']['artists'][0]['name']}"
            )
        else:
            print("❌ No active playback after 'previous' command")

        # Test pause/resume
        print("\n4. Testing pause command...")
        pause_result = player_controls("pause")
        if pause_result["success"]:
            print(f"✅ Pause command succeeded: {pause_result['message']}")
        else:
            print(f"❌ Pause command failed: {pause_result['message']}")

        # Wait a moment
        time.sleep(2)

        print("\n5. Testing resume command...")
        resume_result = player_controls("resume")
        if resume_result["success"]:
            print(f"✅ Resume command succeeded: {resume_result['message']}")
        else:
            print(f"❌ Resume command failed: {resume_result['message']}")

        print("\nTest completed! ✨")

    except Exception as e:
        print(f"❌ Error during test: {str(e)}")


if __name__ == "__main__":
    test_player_flow()
