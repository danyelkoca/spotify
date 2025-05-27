# Spotify POC Project

This repository contains a proof of concept (POC) application that interacts with the Spotify API using Python.

## Project Overview

This project aims to demonstrate capabilities of working with the Spotify API, including authentication, fetching user data, and interacting with Spotify's music library.

## Prerequisites: Spotify Developer Setup

Before starting the implementation, you need to set up a Spotify Developer account and create an application:

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account or create a new account
3. Click on "Create an App" button
4. Fill in the required information:
   - App name: Choose a name for your application (e.g., "Spotify POC")
   - App description: Brief description of your project
   - Redirect URI: Enter any valid URL (e.g., `https://example.org/callback`) - you'll use this exact URL later in the authentication flow
5. Accept the terms and conditions and click "Create"
6. After creation, you'll see your app's dashboard with:
   - Client ID: You'll need this for authentication
   - Client Secret: Click "Show Client Secret" to view it
7. Make note of both the Client ID and Client Secret as you'll need them in the `.env` file later

> **Note**: The redirect URI can be any valid URL (even if you don't own it) as long as you use the same URI in your code. For example, using `https://example.org/callback` is perfectly fine for development purposes.

## Step-by-Step Tutorial

### 1. Initial Setup

```bash
# Initialize git repository
git init

# Create .gitignore to prevent committing sensitive information
cat > .gitignore << EOL
# Spotify API credentials and tokens
.env
.spotify_token_cache

# Python virtual environment
venv/
__pycache__/
*.py[cod]
.DS_Store
EOL

git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/danyelkoca/spotify.git
git push -u origin main
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Required Dependencies

```bash
# Create requirements.txt file with dependencies
cat > requirements.txt << EOL
spotipy==2.23.0
python-dotenv==1.0.0
openai>=1.6.1
EOL

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

## Project Structure

```
spotify/
├── venv/                 # Python virtual environment
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (API credentials)
├── .gitignore            # Prevents sensitive files from being committed
├── .spotify_token_cache  # Cached authentication token
├── README.md             # This documentation file
├── auth.py               # Authentication module
├── spotify_assistant.py  # Natural language Spotify assistant
├── function_schemas.py   # Tool definitions for OpenAI
└── tools/                # Folder with modular functions for the assistant
    ├── __init__.py       # Make tools importable
    ├── search_songs.py   # Search functionality
    ├── get_top_songs.py  # Get user's top tracks
    ├── play_song.py      # Play functionality
    └── player_controls.py # Additional controls (pause, skip, etc.)
```

## Technology Stack

- Python 3
- spotipy==2.23.0 (Spotify API Python client)
- openai>=1.6.1 (OpenAI API for natural language processing)
- python-dotenv==1.0.0 (Environment variable management)
- Virtual Environment (venv)

### 4. Spotify API Authentication Setup

```bash
# Create a .env file to store Spotify API credentials
cat > .env << EOL
# Spotify API Credentials
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=https://example.org/callback
OPENAI_API_KEY=your_openai_api_key_here
EOL
```

To get your Spotify API credentials:

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account
3. Click "Create An App"
4. Fill in the app name and description
5. Once created, you'll see your Client ID and you can view your Client Secret
6. Click "Edit Settings" and add `https://example.org/callback` as a Redirect URI
   - Make sure there are no leading/trailing spaces
   - The URI format must be exactly as shown, including the http:// or https:// part
7. Update the `.env` file with your actual Client ID and Client Secret
8. If you receive an "INVALID_CLIENT" error, double-check that your redirect URI in the Spotify Dashboard matches exactly with the one in your `.env` file

### 5. Running the Application

```bash
# Run the natural language Spotify assistant
python spotify_assistant.py
```

With the assistant, you can perform operations like:

- "Search for songs by The Beatles"
- "Play my top songs from the last 6 months"
- "Play the song Bohemian Rhapsody"
- "Pause the music" or "Skip to the next track"

## Natural Language Spotify Assistant

The core of this project is the natural language assistant that allows you to interact with Spotify using conversational language. The assistant:

- Uses OpenAI's function calling to parse user requests into Spotify API calls
- Supports multi-step interactions through recursive tool calls
- Provides a user-friendly interface for all Spotify operations
- Maintains conversation context for improved user experience

### Available Features

1. **Search for Songs**: Find songs by title, artist, album, or genre
2. **Get Top Songs**: View your most played tracks over different time periods
3. **Play Songs**: Start playback of specific songs or from search results
4. **Playback Control**: Pause, resume, skip tracks, and manage playback

### Technical Implementation

The assistant uses a modular architecture:

- `function_schemas.py` defines the available tools for OpenAI
- `tools/` directory contains modular implementation of each Spotify API feature
- `spotify_assistant.py` handles the conversation flow and OpenAI integration

#### Authentication Process

**Note:** Authentication is required in the following situations:

1. When running the application for the first time
2. When the cached token expires (usually after 1 hour)
3. When you change the scope of permissions (e.g., adding new API features that require different permissions)

When authentication is needed, you'll need to:

1. Follow the authorization URL that appears in the terminal
2. Allow the app access to your Spotify account
3. You'll be redirected to a page that may show an error (this is expected since there's no actual server running at the redirect URI)
4. Copy the **COMPLETE** URL from your browser's address bar (it will look like `https://example.org/callback?code=AQA...`)
5. Paste this entire URL back in the terminal prompt

After successful authentication, a token cache file will be created. Subsequent runs will use this cached token automatically until it expires.

**Troubleshooting Authentication Issues:**

- If you get an "invalid_grant" error, try the process again immediately - authorization codes expire quickly
- Make sure the redirect URI in your .env file exactly matches what's registered in your Spotify Developer Dashboard
- The application will retry authentication up to 3 times if there are issues

## Next Steps

- Add more Spotify API functionality
- Create a web interface with Flask
- Implement data visualization for music statistics

## Development Log

- May 27, 2025: Initial project setup, created GitHub repository
- May 27, 2025: Created Python virtual environment and project structure
- May 27, 2025: Implemented Spotify OAuth authentication using environment variables
- May 27, 2025: Added song search functionality and playback by song ID
- May 27, 2025: Created natural language assistant with OpenAI integration
- May 27, 2025: Refactored code into modular components in the tools/ directory
- May 27, 2025: Improved the OpenAI client integration and fixed recursive tool calls
- May 27, 2025: Streamlined project structure by removing redundant standalone scripts
