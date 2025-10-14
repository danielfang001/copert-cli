"""LangChain ChatOpenAI client wrapper."""

from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool

from copert.config import settings


class CopertLLM:
    """Wrapper for LangChain ChatOpenAI client with tool binding support."""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        streaming: bool = True,
    ):
        """Initialize the Copert LLM client.

        Args:
            model: OpenAI model name (defaults to settings.openai_model)
            temperature: Temperature for response generation (defaults to settings.openai_temperature)
            max_tokens: Maximum tokens in response (defaults to settings.openai_max_tokens)
            streaming: Enable streaming responses
        """
        self.model_name = model or settings.openai_model
        self.temperature = temperature if temperature is not None else settings.openai_temperature
        self.max_tokens = max_tokens or settings.openai_max_tokens
        self.streaming = streaming

        # Initialize ChatOpenAI
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            streaming=streaming,
            api_key=settings.openai_api_key,
        )

    def bind_tools(self, tools: List[BaseTool]) -> BaseChatModel:
        """Bind tools to the LLM for function calling.

        Args:
            tools: List of LangChain BaseTool instances

        Returns:
            ChatOpenAI instance with tools bound
        """
        return self.llm.bind_tools(tools)

    def get_llm(self) -> ChatOpenAI:
        """Get the underlying ChatOpenAI instance.

        Returns:
            ChatOpenAI instance
        """
        return self.llm

    def invoke(self, messages):
        """Invoke the LLM with messages.

        Args:
            messages: List of message objects or a string

        Returns:
            AIMessage with the response
        """
        return self.llm.invoke(messages)

    async def ainvoke(self, messages):
        """Asynchronously invoke the LLM with messages.

        Args:
            messages: List of message objects or a string

        Returns:
            AIMessage with the response
        """
        return await self.llm.ainvoke(messages)


def create_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    streaming: bool = True,
) -> CopertLLM:
    """Factory function to create a CopertLLM instance.

    Args:
        model: OpenAI model name
        temperature: Temperature for response generation
        streaming: Enable streaming responses

    Returns:
        CopertLLM instance
    """
    return CopertLLM(
        model=model,
        temperature=temperature,
        streaming=streaming,
    )
