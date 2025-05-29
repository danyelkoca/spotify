TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information about music, artists, festivals, or any other topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_songs",
            "description": "Search for songs on Spotify by name, artist, or other keywords",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for songs",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 1 for specific songs, increase for browsing/discovery)",
                        "default": 1,
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_songs",
            "description": "Get user's saved tracks (liked songs) from Spotify. Results are cached for faster access.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of songs to return (default: 50, max: 50)",
                        "default": 50,
                        "minimum": 1,
                        "maximum": 50,
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_song",
            "description": "Play a specific song by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "track_id": {
                        "type": "string",
                        "description": "Spotify track ID",
                    }
                },
                "required": ["track_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "player_controls",
            "description": "Control Spotify playback (pause, resume, skip, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "pause",
                            "resume",
                            "next",
                            "previous",
                            "shuffle",
                            "repeat",
                        ],
                    }
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_devices",
            "description": "List all available Spotify devices that can be used for playback",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]
