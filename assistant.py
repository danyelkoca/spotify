import os
import json
import argparse
import logging
from openai import OpenAI
from dotenv import load_dotenv
from core.logger import log_execution, SpotifyLogger

# Import function schemas and tools
from schemas.function_schemas import TOOL_SCHEMAS
from function_tools.search_songs import search_songs
from function_tools.play_song import play_song
from function_tools.player_controls import player_controls
from function_tools.get_songs import get_songs
from function_tools.web_search import web_search


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Spotify Assistant")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="ERROR",
        help="Set the logging level (default: ERROR)",
    )
    return parser.parse_args()


# Initialize logging
logger = SpotifyLogger.get_logger()

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()


@log_execution
def handle_conversation():
    """Main conversation loop for Spotify Assistant"""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful Spotify assistant. You can search for songs, play music, control playback, access liked songs, and search the web. "
                "Keep responses extremely brief (1-2 short sentences max). Use a casual, friendly tone. "
                "IMPORTANT BEHAVIORS:\n"
                "1. For web search results:\n"
                "   - After getting web search results, IMMEDIATELY:\n"
                "     * For festivals/concerts: Extract headlining artists and search their songs\n"
                "     * For artist info: Search their top songs\n"
                "   - Don't wait for user confirmation, proceed directly to search_songs\n"
                "2. When searching songs:\n"
                "   - Show search results to user with artist names\n"
                "   - When user wants to play music, automatically play top result\n"
                "3. For multi-step interactions:\n"
                "   - Always complete the full flow (e.g., web_search → search_songs → play_song)\n"
                "   - Don't stop after intermediate steps\n"
                "IMPORTANT SEARCH AND PLAY BEHAVIOR:\n"
                "1. When user requests a SPECIFIC song:\n"
                "   - ALWAYS include both song title AND artist in query\n"
                "   - From search results, select the exact song user requested\n"
                "   - Consider both song name match and popularity\n"
                "   - Examples:\n"
                "     * For 'play never gonna give you up' → search 'never gonna give you up Rick Astley', pick the original song\n"
                "     * For 'play bohemian rhapsody' → search 'bohemian rhapsody Queen', pick Bohemian Rhapsody (not other Queen songs)\n"
                "     * For 'play thriller' → search 'thriller Michael Jackson', pick the original Thriller\n"
                "2. When user wants to BROWSE or DISCOVER music:\n"
                "   - Results are already sorted by popularity\n"
                "   - Show users multiple options with artist names\n"
                "   - Example: 'find me some rock songs' or 'search for dance music'\n"
                "Always complete the play_song step after searching if the user wants to play music.\n"
                "When searching without playing, list artist and song names in results. "
                "When user asks about favorite songs, liked songs, top songs, or music collection - use get_songs. "
                "For questions about current music events, festivals, or artists - use web_search to get current information, ALWAYS show the search results to the user, "
                "then offer to play music from discovered artists if relevant. Use search_songs and play_song when the user wants to play music from search results. "
                "Avoid unnecessary explanations, greetings, or verbose descriptions."
            ),
        }
    ]

    # Check if SERPAPI_KEY is set
    if not os.getenv("SERPAPI_KEY"):
        logger.warning("SERPAPI_KEY not set in .env file")
        print("\n⚠️ Warning: SERPAPI_KEY not set in .env file")
        print("Web search functionality will not work.\n")

    print("\n✨ Spotify Assistant ✨")
    print("--------------------------------------------")
    print("Ask me anything about Spotify or to play music!")
    print("(Type 'exit' to quit)\n")

    while True:
        # Get user input
        user_input = input("👤 You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            logger.info("User requested to exit")
            print("\nGoodbye! Enjoy your music! 🎵")
            break

        # Add user message to conversation
        messages.append({"role": "user", "content": user_input})
        logger.debug(f"Received user input: {user_input}")

        try:
            # Get response from OpenAI with our tools
            logger.debug("Sending request to OpenAI")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOL_SCHEMAS,
            )

            # Get the assistant's response
            assistant_message = response.choices[0].message
            logger.debug("Received response from OpenAI")

            # Check if the model wants to use a tool
            tool_call = None
            if assistant_message.tool_calls:
                tool_call = assistant_message.tool_calls[0]
                logger.info(
                    f"Assistant requesting to use tool: {tool_call.function.name}"
                )

                # Add assistant's message with tool call to the conversation
                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.content or "",
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
                    logger.debug(
                        f"Function call: {function_name} with args: {arguments}"
                    )

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
                    elif function_name == "player_controls":
                        print(f"\n⏯️ Controlling playback...")
                        result = player_controls(**arguments)
                    elif function_name == "web_search":
                        print(f"\n🌍 Searching the web...")
                        result = web_search(**arguments)
                        if result.get("success") and result.get("results"):
                            print("\nSearch Results:")
                            for idx, item in enumerate(result["results"], 1):
                                print(f"\n{idx}. {item['title']}")
                                print(f"   {item['snippet']}")

                    logger.debug(f"Function result: {result}")

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
                logger.debug("Getting final response from OpenAI")
                final_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                )

                # Check if another tool call is needed (e.g., after search_songs → play_song)
                assistant_message = final_response.choices[0].message
                if assistant_message.tool_calls:
                    logger.info("Assistant wants to make another tool call in sequence")

                    # Get the first tool call only
                    tool_call = assistant_message.tool_calls[0]

                    # Add the assistant's message with tool call
                    messages.append(
                        {
                            "role": "assistant",
                            "content": assistant_message.content or "",
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

                    # Parse and execute the function
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    logger.debug(
                        f"Follow-up function call: {function_name} with args: {arguments}"
                    )

                    # Execute the appropriate function
                    result = None
                    if function_name == "search_songs":
                        print(f"\n🔍 Searching for songs...")
                        result = search_songs(**arguments)
                        if result.get("success") and result.get("tracks"):
                            print("\nFound these songs:")
                            for idx, track in enumerate(result["tracks"][:5], 1):
                                print(f"{idx}. {track['name']} by {track['artist']}")

                            # Auto-play if this was a play request
                            if any(
                                word in user_input.lower()
                                for word in ["play", "listen", "hear"]
                            ):
                                top_track = result["tracks"][0]
                                play_result = play_song(track_id=top_track["id"])
                                if play_result and play_result.get("success"):
                                    result = play_result
                    elif function_name == "get_songs":
                        print(f"\n🎵 Fetching your music collection...")
                        result = get_songs(**arguments)
                    elif function_name == "play_song":
                        print(f"\n▶️ Playing music...")
                        result = play_song(**arguments)
                    elif function_name == "player_controls":
                        print(f"\n⏯️ Controlling playback...")
                        result = player_controls(**arguments)
                    elif function_name == "web_search":
                        print(f"\n🌍 Searching the web...")
                        result = web_search(**arguments)
                        if result.get("success") and result.get("results"):
                            print("\nSearch Results:")
                            for idx, item in enumerate(result["results"], 1):
                                print(f"\n{idx}. {item['title']}")
                                print(f"   {item['snippet']}")

                    logger.debug(f"Follow-up function result: {result}")

                    # Add the tool result to conversation
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

                    # Get the final response after tool call
                    logger.debug("Getting final response after follow-up action")
                    final_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                    )

                # Display the assistant's final response
                final_message = final_response.choices[0].message.content or ""
                # Include the result message for playback or specific functions
                if result:
                    if function_name in ["play_song"] and result.get("success"):
                        logger.info(f"Playback result: {result['message']}")
                        print(f"🎵 Assistant: {result['message']}")
                    elif function_name == "get_songs" and result.get("success"):
                        total_songs = len(result.get("tracks", []))
                        sources = ", ".join(result.get("sources", []))
                        songs_info = f"Found {total_songs} songs in: {sources}"
                        logger.info(songs_info)
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
                logger.info(f"Assistant response: {assistant_message}")
                print(f"🎵 Assistant: {assistant_message}")
                messages.append(response.choices[0].message)

        except Exception as e:
            logger.error(f"Error in conversation handler: {str(e)}", exc_info=True)
            print(f"⚠️ Error occurred: {str(e)}")
            print("🎵 Assistant: Sorry, something went wrong. Let's try again.")


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()

    # Set log level from command line argument
    log_level = getattr(logging, args.log_level)
    SpotifyLogger().set_level(log_level)

    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is not set")
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        exit(1)

    logger.info("Starting Spotify Assistant")
    handle_conversation()
