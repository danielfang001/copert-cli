from langchain import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from weather_tool import WeatherTool
import os

# Initialize the chat model
chat_model = ChatOpenAI(temperature=0)

# Set up memory to keep track of the conversation
memory = ConversationBufferMemory()

# Create a conversation chain with the chat model and memory
conversation_chain = ConversationChain(
    llm=chat_model,
    memory=memory
)

# Initialize weather tool with API key from env
weather_api_key = os.getenv("WEATHER_API_KEY", "")
weather_tool = WeatherTool(api_key=weather_api_key)

# Function to interact with the chatbot with weather integration
def chat_with_weather_bot(user_input):
    # Check if user asks for weather
    if user_input.lower().startswith("weather in"):
        city = user_input[10:].strip()
        weather_info = weather_tool.get_weather(city)
        return weather_info
    # Else normal chat
    response = conversation_chain.run(user_input)
    return response


# Example interaction
if __name__ == '__main__':
    user_input = "weather in New York"
    print(chat_with_weather_bot(user_input))
