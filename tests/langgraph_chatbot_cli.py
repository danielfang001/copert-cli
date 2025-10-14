import argparse
from langchain import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from weather_tool import WeatherTool
import os

from langgraph import ChatGraph

# Initialize the chat model
chat_model = ChatOpenAI(temperature=0)

# Set up memory to keep track of the conversation
memory = ConversationBufferMemory()

# Create a conversation chain
conversation_chain = ConversationChain(
    llm=chat_model,
    memory=memory
)

# Initialize weather tool with API key from env
weather_api_key = os.getenv("WEATHER_API_KEY", "")
weather_tool = WeatherTool(api_key=weather_api_key)

# Function to handle chat input and optionally use weather tool

def chatbot_response(user_input: str) -> str:
    # If user wants weather, parse city and use the weather tool
    if user_input.lower().startswith("weather in"):
        city = user_input[10:].strip()
        weather_info = weather_tool.get_weather(city)
        return weather_info
    # Otherwise, use conversation chain
    response = conversation_chain.run(user_input)
    return response


# Build LangGraph chat graph
chat_graph = ChatGraph()
chat_graph.add_function(chatbot_response, name="chatbot_response")


def main():
    parser = argparse.ArgumentParser(description="Chatbot CLI with weather tool")
    parser.add_argument("--input", type=str, required=True, help="User input message")
    args = parser.parse_args()

    response = chat_graph.call("chatbot_response", args.input)
    print(response)


if __name__ == '__main__':
    main()
