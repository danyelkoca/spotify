import webbrowser
import time
import sys
from auth import get_token
import spotipy


def get_track_info(sp, track_id=None):
    """
    Get track information either from a provided track ID or the user's top track

    Args:
        sp: Spotify client
        track_id: Optional track ID or URI

    Returns:
        tuple: (track_name, artist_name, track_uri, track_url)
    """
    if track_id:
        # Check if it's a full URI or just an ID
        if track_id.startswith("spotify:track:"):
            track_uri = track_id
            track_id = track_id.split(":")[-1]
        else:
            track_uri = f"spotify:track:{track_id}"

        # Get track info from the ID
        try:
            track = sp.track(track_id)
            track_name = track["name"]
            artist_name = track["artists"][0]["name"]
            track_url = track["external_urls"]["spotify"]
            return track_name, artist_name, track_uri, track_url
        except Exception as e:
            print(f"Error retrieving track with ID {track_id}: {e}")
            return None, None, None, None
    else:
        # Get user's top track
        top_tracks = sp.current_user_top_tracks(limit=1, time_range="short_term")

        if not top_tracks["items"]:
            print("No top tracks found. Try listening to more music on Spotify!")
            return None, None, None, None

        top_track = top_tracks["items"][0]
        track_name = top_track["name"]
        artist_name = top_track["artists"][0]["name"]
        track_uri = top_track["uri"]
        track_url = top_track["external_urls"]["spotify"]
        return track_name, artist_name, track_uri, track_url


def play_song(track_id=None):
    """Play a song on an available Spotify device

    Args:
        track_id: Optional track ID or URI. If not provided, plays user's top song
    """
    print("Spotify Player")
    print("------------------------")

    try:
        # Get authentication token
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Get track information
        track_name, artist_name, track_uri, track_url = get_track_info(sp, track_id)

        if not track_uri:
            return

        # Get available devices
        devices = sp.devices()

        if not devices["devices"]:
            print("No active Spotify devices found. Opening in browser instead...")
            print(f"\nSelected track: {track_name} by {artist_name}")
            webbrowser.open(track_url)
            return

        # Use the first available device
        device_id = devices["devices"][0]["id"]
        device_name = devices["devices"][0]["name"]

        print(f"\nSelected track: {track_name} by {artist_name}")
        print(f"Playing on {device_name}...")

        # Start playback on the device
        sp.start_playback(device_id=device_id, uris=[track_uri])

        # Wait a moment to ensure playback has started
        time.sleep(1)

        # Get current playback to confirm
        playback = sp.current_playback()
        if playback and playback.get("is_playing"):
            print("✓ Now playing!")
        else:
            print("Could not confirm playback. Opening in browser instead...")
            webbrowser.open(track_url)

    except spotipy.exceptions.SpotifyException as e:
        if "NO_ACTIVE_DEVICE" in str(e):
            print("No active Spotify devices found. Opening in browser instead...")
            webbrowser.open(track_url)
        else:
            print(f"Spotify Error: {e}")
            print("Opening track in browser instead...")
            webbrowser.open(track_url)
    except Exception as e:
        print(f"Error: {e}")
        print("Opening track in browser as fallback...")
        if "track_url" in locals():
            webbrowser.open(track_url)


def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) > 1:
        # If an argument is provided, use it as a track ID
        track_id = sys.argv[1]
        play_song(track_id)
    else:
        # Otherwise play the user's top song
        play_song()


if __name__ == "__main__":
    main()
