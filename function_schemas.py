TOOL_SCHEMAS = [
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
                        "description": "Maximum number of results to return",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_songs",
            "description": "Get the user's top tracks from Spotify",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "string",
                        "enum": ["short_term", "medium_term", "long_term"],
                        "description": "Time range for top tracks: short_term (4 weeks), medium_term (6 months), or long_term (years)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of tracks to return",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_song",
            "description": "Play a specific song by ID or URI",
            "parameters": {
                "type": "object",
                "properties": {
                    "track_id": {
                        "type": "string",
                        "description": "Spotify track ID or URI",
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
]
