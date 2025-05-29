# Spotify Voice Assistant

An intelligent voice assistant that interacts with Spotify, combining natural language understanding with music playback control. The assistant can manage your music, search for songs, and provide information about artists and events.

## Key Features

### Intelligent Music Collection

- Unified access to liked songs and top tracks through single interface
- Smart caching system for faster subsequent access
- Automatic duplicate removal across all music sources
- Source tracking for each track in your collection

### Natural Language Control

- Simple conversational interface
- Smart context handling
- Remembers user preferences
- Provides concise, relevant responses

### Web Integration

- Searches multiple sources for current music information
- Finds information about artists, festivals, and events
- Uses search results to find and play relevant music

### Performance Optimization

## Caching System

The application uses an intelligent caching system to improve performance. Here are the test results:

```
First call (uncached):
Time taken: 0.31 seconds
- Fetches data from Spotify API
- Memory usage: ~2.45MB

Second call (cached):
Time taken: 0.00 seconds
- Instant retrieval from cache
- Minimal memory impact: ~0.00MB

Performance Improvement:
- Time saved by caching: 0.31 seconds
- Speed improvement: 1146.3x faster
- Zero API calls on cache hits
```

### Device Selection

The application uses an intelligent device selection system to ensure playback starts on the most appropriate device:

- Prioritizes desktop Spotify clients over mobile devices and web players
- Automatically selects the best available device for playback
- Falls back to web browser if no active devices are available
- Provides a consistent playback experience across multiple devices

### Other Optimizations

- Batch processing for API calls
- Memory-efficient data handling
- Automatic duplicate removal
- Smart pagination for large collections

## Project Structure

```
spotify/
├── venv/                  # Python virtual environment
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (API credentials)
├── .gitignore           # Prevents sensitive files from being committed
├── README.md            # This documentation file
├── auth.py              # Authentication module
├── assistant.py         # Natural language Spotify assistant
├── function_schemas.py  # Tool definitions for OpenAI
└── tools/               # Folder with modular functions for the assistant
    ├── __init__.py      # Make tools importable
    ├── search_songs.py  # Search for songs on Spotify
    ├── get_songs.py     # Unified music collection access (with caching)
    ├── play_song.py     # Play music functionality
    ├── player_controls.py# Playback controls (pause, skip, etc.)
    └── web_search.py    # Search the web for music information
```

## Prerequisites: Spotify Developer Setup

Before starting the implementation, you need to set up a Spotify Developer account and create an application:

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account or create a new account
3. Click on "Create an App" button
4. Fill in the required information:
   - App name: Choose a name for your application (e.g., "Spotify Voice Assistant")
   - App description: Brief description of your project
   - Redirect URI: Enter any valid URL (e.g., `https://example.org/callback`) - you'll use this exact URL later in the authentication flow
5. Accept the terms and conditions and click "Create"
6. After creation, you'll see your app's dashboard with:
   - Client ID: You'll need this for authentication
   - Client Secret: Click "Show Client Secret" to view it
7. Save both the Client ID and Client Secret for use in the `.env` file

> **Note**: The redirect URI can be any valid URL (even if you don't own it) as long as you use the same URI in your code.

## Step-by-Step Tutorial

### 1. Initial Setup

First, create a new directory for your project and navigate to it:

```bash
mkdir spotify-assistant
cd spotify-assistant
```

Initialize a git repository and set up `.gitignore`:

```bash
# Initialize git repository
git init

# Create .gitignore to prevent committing sensitive information
cat > .gitignore << EOL
# Python virtual environment
venv/
__pycache__/
*.py[cod]
.DS_Store
EOL

# Add .gitignore to repository
git add .gitignore
git commit -m "Initial commit: Add .gitignore"
```

### 2. Python Environment Setup

1. Ensure you have Python 3.8 or newer installed:

```bash
python3 --version
```

2. Create and activate a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

3. Verify the virtual environment is active (should show path to venv):

```bash
which python
```

### 3. Dependencies Installation

1. Create a `requirements.txt` file with required packages:

```bash
cat > requirements.txt << EOL
spotipy>=2.23.0
openai>=1.3.0
python-dotenv>=1.0.0
EOL
```

2. Install the required packages:

```bash
pip install -r requirements.txt

# Verify installations
pip list | grep -E "spotipy|openai|python-dotenv"
```

### 4. Environment Configuration

1. Create a `.env` file with your credentials:

```bash
cat > .env << EOL
SPOTIPY_CLIENT_ID='your_client_id'
SPOTIPY_CLIENT_SECRET='your_client_secret'
SPOTIPY_REDIRECT_URI='https://example.org/callback'
OPENAI_API_KEY='your_openai_api_key'
EOL
```

2. Edit the `.env` file and replace the placeholder values with your actual credentials:

- Replace `your_client_id` with your Spotify Client ID
- Replace `your_client_secret` with your Spotify Client Secret
- Replace `your_openai_api_key` with your OpenAI API key
- Keep or modify the redirect URI as needed

3. Verify the `.env` file is properly configured:

```bash
# Should show your credentials (be careful with this in shared environments)
cat .env
```

### 5. Running the Assistant

1. Start the assistant:

```bash
# Make sure your virtual environment is active
python assistant.py
```

2. On first run, you'll need to authenticate with Spotify:

- A browser window will open
- Log in to your Spotify account
- Authorize the application
- You'll be redirected to your callback URL
- The assistant will then be ready to use

3. Verify the assistant is working:

- Try a simple command like "What's playing now?"
- If you get a response, the setup is complete!

## Usage

The assistant responds to natural language commands such as:

- "Play my favorite songs"
- "Show me my top tracks"
- "Play something by [artist]"
- "What's this song about?"
- "Skip this track"
- "Pause the music"

The assistant will handle these requests intelligently, using cached data when possible for better performance.

## Changelog

### v1.0.0 (2025-05-27)

- Consolidated song collection functionality into a unified interface
- Implemented smart caching system for better performance
- Added source tracking for music collection
- Improved duplicate detection and removal
- Streamlined project structure
