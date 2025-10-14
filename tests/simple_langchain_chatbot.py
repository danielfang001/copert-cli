from langchain import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Initialize the chat model
chat_model = ChatOpenAI(temperature=0)

# Set up memory to keep track of the conversation
memory = ConversationBufferMemory()

# Create a conversation chain with the chat model and memory
conversation_chain = ConversationChain(
    llm=chat_model,
    memory=memory
)

# Function to interact with the chatbot
def chat_with_bot(user_input):
    response = conversation_chain.run(user_input)
    return response

# Example interaction
if __name__ == '__main__':
    user_input = "Hello, how are you?"
    bot_response = chat_with_bot(user_input)
    print(bot_response)
