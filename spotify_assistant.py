import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Import function schemas
from function_schemas import TOOL_SCHEMAS

# Import our tools
from tools.search_songs import search_songs
from tools.get_top_songs import get_top_songs
from tools.play_song import play_song
from tools.player_controls import player_controls

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
                "You are a helpful Spotify assistant. You can search for songs, play music, and control playback. "
                "Be concise and friendly in your responses. When playing songs, confirm the action has been taken. "
                "When searching for songs, summarize the results briefly. "
                "Respond in a conversational manner but keep responses short and focused."
            ),
        }
    ]

    print("\n✨ Spotify Voice Assistant ✨")
    print("--------------------------------------------")
    print("Ask me anything about Spotify or to play music!")
    print("(Type 'exit' to quit)\n")

    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nGoodbye! Enjoy your music! 🎵")
            break

        # Add user message to conversation
        messages.append({"role": "user", "content": user_input})

        try:
            # Get response from OpenAI with our tools
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=TOOL_SCHEMAS,
            )

            # Check if the model wants to use a tool
            tool_call = None
            if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                # Add assistant's message with tool call to the conversation
                messages.append(
                    {
                        "role": "assistant",
                        "content": response.choices[0].message.content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments,
                                },
                            }
                        ],
                    }
                )

                # Parse arguments
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                # Execute the appropriate function
                result = None
                if function_name == "search_songs":
                    print(
                        f"\nSearching for songs matching '{arguments.get('query')}'..."
                    )
                    result = search_songs(**arguments)
                elif function_name == "get_top_songs":
                    time_range = arguments.get("time_range", "short_term")
                    print(f"\nGetting your top tracks from {time_range}...")
                    result = get_top_songs(**arguments)
                elif function_name == "play_song":
                    track_id = arguments.get("track_id")
                    print(f"\nPlaying song with ID {track_id}...")
                    result = play_song(**arguments)
                elif function_name == "player_controls":
                    action = arguments.get("action")
                    print(f"\nControlling playback: {action}...")
                    result = player_controls(**arguments)

                # Format the result as JSON string
                result_str = json.dumps(result)

                # Send the function result back to the model
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_str,
                    }
                )

                # Get the final response with the function result
                final_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                )

                # Check if there's another tool call in the response
                if final_response.choices[0].message.tool_calls:
                    # Handle the recursive tool call
                    second_tool_call = final_response.choices[0].message.tool_calls[0]
                    second_function_name = second_tool_call.function.name
                    second_arguments = json.loads(second_tool_call.function.arguments)

                    print(
                        f"\nPerforming additional action: {second_function_name} with {second_arguments}..."
                    )

                    # Execute the second tool call
                    second_result = None
                    if second_function_name == "search_songs":
                        second_result = search_songs(**second_arguments)
                    elif second_function_name == "get_top_songs":
                        second_result = get_top_songs(**second_arguments)
                    elif second_function_name == "play_song":
                        second_result = play_song(**second_arguments)
                    elif second_function_name == "player_controls":
                        second_result = player_controls(**second_arguments)

                    # Add both the tool call and the result to messages
                    messages.append(
                        {
                            "role": "assistant",
                            "content": final_response.choices[0].message.content,
                            "tool_calls": [
                                {
                                    "id": second_tool_call.id,
                                    "type": "function",
                                    "function": {
                                        "name": second_function_name,
                                        "arguments": second_tool_call.function.arguments,
                                    },
                                }
                            ],
                        }
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": second_tool_call.id,
                            "content": json.dumps(second_result),
                        }
                    )

                    # Get the final final response
                    final_final_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        tools=TOOL_SCHEMAS,
                    )

                    assistant_message = final_final_response.choices[0].message.content
                else:
                    assistant_message = final_response.choices[0].message.content

                # Display the assistant's final response
                print(f"Assistant: {assistant_message or 'I processed your request.'}")
                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message or "I processed your request.",
                    }
                )
            else:
                # Regular response (no function call)
                assistant_message = response.choices[0].message.content
                print(f"Assistant: {assistant_message}")
                messages.append({"role": "assistant", "content": assistant_message})

        except Exception as e:
            print(f"Error: {str(e)}")
            print("Assistant: I'm sorry, I encountered an error. Please try again.")


if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        exit(1)

    handle_conversation()
