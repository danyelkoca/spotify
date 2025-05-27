import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Import function schemas
from function_schemas import TOOL_SCHEMAS

# Import our tools
from tools.search_songs import search_songs
from tools.play_song import play_song
from tools.play_song_by_name import play_song_by_name
from tools.player_controls import player_controls
from tools.get_songs import get_songs
from tools.web_search import web_search

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()


def handle_conversation():
    """Main conversation loop for Spotify Voice Assistant"""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful Spotify assistant. You can search for songs, play music, control playback, access liked songs, and search the web. "
                "Keep responses extremely brief (1-2 short sentences max). Use a casual, friendly tone. "
                "When user wants to play a song, use play_song_by_name and pass the full song name with artist (e.g., 'Song Title by Artist Name'). "
                "For exact song matches, always include both song title and artist name in the format 'Title by Artist'. "
                "When searching without playing, just list artist and song names. "
                "When user asks about favorite songs, liked songs, top songs, or music collection - use get_songs. "
                "For questions about current music events, festivals, or artists - use web_search to get current information, then use search_songs or play_song based on the results. "
                "Avoid unnecessary explanations, greetings, or verbose descriptions."
            ),
        }
    ]

    # Check if SERPAPI_KEY is set
    if not os.getenv("SERPAPI_KEY"):
        print("\n⚠️ Warning: SERPAPI_KEY not set in .env file")
        print("Web search functionality will not work.\n")

    print("\n✨ Spotify Voice Assistant ✨")
    print("--------------------------------------------")
    print("Ask me anything about Spotify or to play music!")
    print("(Type 'exit' to quit)\n")

    while True:
        # Get user input
        user_input = input("👤 You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nGoodbye! Enjoy your music! 🎵")
            break

        # Add user message to conversation
        messages.append({"role": "user", "content": user_input})

        try:
            # Get response from OpenAI with our tools
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOL_SCHEMAS,
            )

            # Get the assistant's response
            assistant_message = response.choices[0].message

            # Check if the model wants to use a tool
            tool_call = None
            if assistant_message.tool_calls:
                tool_call = assistant_message.tool_calls[0]
                # Add assistant's message with tool call to the conversation
                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.content
                        or "",  # Handle null content
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": tool_call.type,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments,
                                },
                            }
                        ],
                    }
                )

                # Handle function tools
                if tool_call.type == "function":
                    # Parse arguments
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Execute the appropriate function
                    result = None
                    if function_name == "search_songs":
                        print(f"\n🔍 Searching for songs...")
                        result = search_songs(**arguments)
                    elif function_name == "get_songs":
                        print(f"\n🎵 Fetching your music collection...")
                        result = get_songs(**arguments)
                    elif function_name == "play_song":
                        print(f"\n▶️ Playing music...")
                        result = play_song(**arguments)
                    elif function_name == "play_song_by_name":
                        song_name = arguments.get("song_name")
                        print(f"\n🎵 Finding and playing '{song_name}'...")
                        result = play_song_by_name(**arguments)
                    elif function_name == "player_controls":
                        action = arguments.get("action")
                        print(f"\n⏯️ Controlling playback...")
                        result = player_controls(**arguments)
                    elif function_name == "web_search":
                        print(f"\n🌍 Searching the web...")
                        result = web_search(**arguments)

                    # Always send a response for the tool call
                    result_str = (
                        json.dumps(result)
                        if result
                        else json.dumps({"error": "No result"})
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_str,
                        }
                    )

                # Get the final response with the function result
                final_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                )

                # Display the assistant's final response
                final_message = final_response.choices[0].message.content or ""
                # Include the result message for playback or specific functions
                if result:
                    if function_name in [
                        "play_song",
                        "play_song_by_name",
                    ] and result.get("success"):
                        print(f"🎵 Assistant: {result['message']}")
                    elif function_name == "get_songs" and result.get("success"):
                        total_songs = len(result.get("tracks", []))
                        sources = ", ".join(result.get("sources", []))
                        songs_info = f"Found {total_songs} songs in: {sources}"
                        if final_message:
                            print(f"🎵 Assistant: {final_message}")
                        else:
                            print(f"🎵 Assistant: {songs_info}")
                    elif result.get("message"):
                        print(f"🎵 Assistant: {result['message']}")
                    else:
                        print(f"🎵 Assistant: {final_message or 'Done!'}")
                else:
                    print(f"🎵 Assistant: {final_message or 'Done!'}")

                # Add the final response to conversation history
                messages.append({"role": "assistant", "content": final_message or ""})
            else:
                # Regular response (no function call)
                assistant_message = response.choices[0].message.content
                print(f"🎵 Assistant: {assistant_message}")
                messages.append(response.choices[0].message)

        except Exception as e:
            print(f"⚠️ Error occurred: {str(e)}")
            print("🎵 Assistant: Sorry, something went wrong. Let's try again.")


if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        exit(1)

    handle_conversation()
