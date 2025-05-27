"""Initialize tools package"""

from .search_songs import search_songs
from .play_song import play_song
from .play_song_by_name import play_song_by_name
from .player_controls import player_controls
from .get_songs import get_songs
from .web_search import web_search

__all__ = [
    "search_songs",
    "play_song",
    "play_song_by_name",
    "player_controls",
    "get_songs",
    "web_search",
]
