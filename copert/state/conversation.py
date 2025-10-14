"""Conversation state management for LangGraph."""

from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State schema for the Copert agent.

    The messages list uses add_messages reducer which intelligently
    appends messages to the list rather than overwriting them.
    """
    messages: Annotated[List[BaseMessage], add_messages]
