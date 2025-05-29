# Spotify Voice Assistant

A voice-controlled Spotify assistant that lets you manage your music, search for songs, and get information about artists and events using natural language.

## Features

- Voice control for Spotify playback (play, pause, skip, etc.)
- Natural language music search and discovery
- Smart caching for faster performance
- Real-time artist and event information
- Automatic device selection and fallback

## Quick Setup

1. **Clone the Repository**:

```bash
git clone https://github.com/danyelkoca/spotify.git
cd spotify
```

2. **Install Python Requirements**:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set Up API Keys**:

Create a `.env` file in the project root with:

```properties
# Spotify API Credentials (from https://developer.spotify.com/dashboard)
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=https://example.org/callback

# OpenAI API Key (from https://platform.openai.com/api-keys)
OPENAI_API_KEY=your_openai_key

# SerpAPI Key for web search (from https://serpapi.com/dashboard)
SERPAPI_KEY=your_serpapi_key
```

4. **Run the Assistant**:

```bash
python assistant.py
```

On first run, you'll need to authenticate with Spotify in your browser.

## Project Structure

```
spotify/
├── core/                  # Core functionality
│   ├── auth.py           # Spotify authentication
│   ├── logger.py         # Logging system
│   └── utils.py          # Shared utilities
├── docs/                 # Documentation
│   └── README.md         # Project documentation
├── function_tools/       # Assistant functions
│   ├── get_songs.py      # Music collection management
│   ├── list_devices.py   # Spotify device management
│   ├── play_song.py      # Music playback
│   ├── player_controls.py # Playback controls
│   ├── search_songs.py   # Music search
│   └── web_search.py     # Web search integration
├── logs/                 # Application logs
│   └── spotify.log       # Runtime logs
├── schemas/              # API schemas
│   └── function_schemas.py# OpenAI function definitions
├── tests/                # Test suites
│   ├── integration/      # Integration tests
│   │   └── test_integrated.py # Integration test cases
│   └── unit/            # Unit tests
│       ├── test_caching.py    # Cache system tests
│       ├── test_device_selection.py # Device management tests
│       └── test_player_controls.py  # Playback control tests
├── .env                  # Environment configuration
├── .gitignore           # Git ignore rules
├── .spotify_token_cache  # Spotify authentication cache
├── assistant.py         # Main assistant application
└── requirements.txt     # Python dependencies
```

## Getting API Keys

### Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new app
3. Get Client ID and Secret
4. Add `https://example.org/callback` as the Redirect URI

### OpenAI API

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (only shown once)

### SerpAPI

1. Go to [SerpAPI Dashboard](https://serpapi.com/dashboard)
2. Sign up and get your API key

## Running the Assistant

The assistant supports commands like:

- "Play [song/artist]"
- "Skip this track"
- "Show my liked songs"
- "What's this song about?"
- "Tell me about [artist]"

### Common Issues

- **No active device**: Open Spotify on any device first
- **Authentication fails**: Double-check your Spotify API credentials
- **Can't play music**: Ensure you have an active Spotify Premium account
