import spotipy
import time
import sys
from core.auth import get_token
from core.logger import SpotifyLogger
from core.utils import get_best_device, ensure_playback
from core.player_controls import player_controls
from core.play_song import play_song
from core.search_songs import search_songs

logger = SpotifyLogger.get_logger()


def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(f"  {message}")
    print("=" * 50)


def test_integrated_flow():
    """
    Test the entire flow including searching, playing, and controlling playback
    to ensure everything works together properly.
    """
    try:
        print_header("SPOTIFY VOICE ASSISTANT INTEGRATION TEST")

        # Get auth token
        token_info = get_token()
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # TEST 1: List devices and select best one
        print_header("1. DEVICE SELECTION")
        device_id, device_name = get_best_device(sp)
        if not device_id:
            print(
                "❌ No devices available for testing. Open Spotify on your device first."
            )
            return 1

        print(f"✅ Selected device: {device_name}")

        # TEST 2: Search for a song
        print_header("2. SEARCH FUNCTIONALITY")
        search_term = "Another One Bites the Dust"
        print(f"Searching for: '{search_term}'")

        search_results = search_songs(search_term)
        if not search_results["success"]:
            print(f"❌ Search failed: {search_results['message']}")
            return 1

        if not search_results["tracks"]:
            print("❌ No tracks found")
            return 1

        # Get first result
        first_track = search_results["tracks"][0]
        print(f"✅ Found: '{first_track['name']}' by {first_track['artist']}")
        track_id = first_track["id"]

        # TEST 3: Play the song
        print_header("3. PLAYBACK FUNCTIONALITY")
        print(f"Playing track: {first_track['name']}")

        play_result = play_song(track_id)
        if not play_result["success"]:
            print(f"❌ Play failed: {play_result['message']}")
            return 1

        print(f"✅ {play_result['message']}")

        # Let it play for a moment
        print("Letting track play for 5 seconds...")
        time.sleep(5)

        # TEST 4: Verify playback is active
        print_header("4. PLAYBACK VERIFICATION")
        playback = sp.current_playback()

        if not playback or not playback.get("is_playing"):
            print("❌ Playback check failed - track not playing")

            # Try to recover
            print("Attempting playback recovery...")
            success, playback = ensure_playback(sp, first_track["id"])

            if not success:
                print("❌ Recovery failed")
                return 1
            else:
                print("✅ Successfully recovered playback")
        else:
            print(f"✅ Currently playing: {playback['item']['name']}")

        # TEST 5: Test player controls
        print_header("5. PLAYBACK CONTROLS")

        # Test pause
        print("Testing pause...")
        pause_result = player_controls("pause")
        if pause_result["success"]:
            print(f"✅ Pause successful: {pause_result['message']}")
        else:
            print(f"❌ Pause failed: {pause_result['message']}")

        # Wait briefly
        time.sleep(2)

        # Test resume
        print("\nTesting resume...")
        resume_result = player_controls("resume")
        if resume_result["success"]:
            print(f"✅ Resume successful: {resume_result['message']}")
        else:
            print(f"❌ Resume failed: {resume_result['message']}")

        # Wait briefly
        time.sleep(2)

        # Test skip
        print("\nTesting next track...")
        next_result = player_controls("next")
        if next_result["success"]:
            print(f"✅ Next track successful: {next_result['message']}")
        else:
            print(f"❌ Next track failed: {next_result['message']}")

        # Check what's playing now
        time.sleep(2)
        playback = sp.current_playback()
        if playback and playback.get("is_playing"):
            print(f"✅ Now playing: {playback['item']['name']}")
        else:
            print("⚠️ No active playback detected after next command")

        # TEST 6: Test previous
        print("\nTesting previous track...")
        prev_result = player_controls("previous")
        if prev_result["success"]:
            print(f"✅ Previous track successful: {prev_result['message']}")
        else:
            print(f"❌ Previous track failed: {prev_result['message']}")

        # Check what's playing now
        time.sleep(2)
        playback = sp.current_playback()
        if playback and playback.get("is_playing"):
            print(f"✅ Now playing: {playback['item']['name']}")
        else:
            print("⚠️ No active playback detected after previous command")

        print_header("TEST COMPLETED SUCCESSFULLY ✨")
        return 0

    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(test_integrated_flow())
