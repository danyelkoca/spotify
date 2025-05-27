import sys
from auth import get_token
import spotipy
import json


def search_songs(query, limit=5):
    """
    Search for songs on Spotify and return detailed information including song IDs

    Args:
        query (str): Search query for songs
        limit (int): Maximum number of results to return

    Returns:
        list: List of songs with their details
    """
    print(f"Searching for: {query}")
    print("------------------------")

    try:
        # Get authentication token
        token_info = get_token()

        # Create a Spotify client
        sp = spotipy.Spotify(auth=token_info["access_token"])

        # Search for tracks
        results = sp.search(q=query, type="track", limit=limit)

        if not results["tracks"]["items"]:
            print(f"No songs found matching '{query}'")
            return []

        # Extract relevant track information
        tracks = []
        for i, track in enumerate(results["tracks"]["items"]):
            track_info = {
                "id": track["id"],
                "uri": track["uri"],
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "duration_ms": track["duration_ms"],
                "popularity": track["popularity"],
                "url": track["external_urls"]["spotify"],
            }
            tracks.append(track_info)

            # Print track information
            print(f"\n{i+1}. {track_info['name']} by {track_info['artist']}")
            print(f"   Album: {track_info['album']}")
            print(
                f"   Duration: {track_info['duration_ms'] // 60000}:{(track_info['duration_ms'] % 60000) // 1000:02d}"
            )
            print(f"   Popularity: {track_info['popularity']}/100")
            print(f"   Song ID: {track_info['id']}")
            print(f"   URI: {track_info['uri']}")
            print(f"   To play this song: python play.py {track_info['id']}")

        return tracks

    except Exception as e:
        print(f"Error: {e}")
        return []


def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Please provide a search query")
        print("Usage: python search.py 'search query' [limit]")
        return

    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    search_songs(query, limit)


if __name__ == "__main__":
    main()
