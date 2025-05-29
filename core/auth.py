import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def create_spotify_oauth():
    """Create and return a SpotifyOAuth instance for authentication"""
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID").strip(),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET").strip(),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI").strip(),
        scope="user-library-read user-top-read user-modify-playback-state user-read-playback-state",
        cache_path=".spotify_token_cache",
    )


def get_token():
    """Get an access token for the Spotify API"""
    sp_oauth = create_spotify_oauth()
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            auth_url = sp_oauth.get_authorize_url()
            print(
                f"Please navigate to this URL to authorize the application:\n{auth_url}"
            )
            print(
                "After authorizing, you'll be redirected to a page that may show an error - this is normal."
            )
            print(
                "Copy the FULL URL from your browser's address bar and paste it here."
            )

            response = input("Enter the URL you were redirected to: ")

            try:
                code = sp_oauth.parse_response_code(response)
                # Use get_access_token without as_dict for future compatibility
                token_info = sp_oauth.get_access_token(code, as_dict=True)
                break
            except Exception as e:
                print(f"Error getting token: {e}")
                print(f"Attempt {attempt} of {max_attempts} failed.")

                if attempt < max_attempts:
                    print("Let's try again.")
                else:
                    print("Maximum attempts reached. Could not authenticate.")
                    raise

    # If we reach here, we have a valid token_info
    return token_info


def main():
    print("Spotify POC Application")
    print("------------------------")

    try:
        # Get token for authentication
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Test the connection by getting the current user's details
        user_info = sp.current_user()
        print(f"Successfully connected to Spotify as {user_info['display_name']}")

        # Get user's top tracks
        top_tracks = sp.current_user_top_tracks(limit=5, time_range="short_term")

        print("\nYour Top 5 Tracks:")
        for i, track in enumerate(top_tracks["items"]):
            print(f"{i+1}. {track['name']} by {track['artists'][0]['name']}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
