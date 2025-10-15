"""LangGraph state graph for the Copert agent."""

from typing import Literal, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from copert.state.conversation import AgentState
from copert.llm import create_llm, COPERT_SYSTEM_PROMPT
from copert.tools import ALL_TOOLS
from copert.utils import ApprovalManager


def create_agent_graph(system_prompt: Optional[str] = None, tools: Optional[List] = None, approval_manager: Optional[ApprovalManager] = None):
    """Create and compile the LangGraph agent graph.

    The graph follows the Claude Code pattern:
    1. User message → agent
    2. Agent decides and makes tool calls → tools
    3. Tools execute and return ToolMessage results → agent
    4. Agent sees results, decide no more tools are needed , and generates summary response → end

    Note: AIMessage can contain both text content and tool_calls.
    When tool_calls are present, we route to tools regardless of content.

    Args:
        system_prompt: Optional custom system prompt (defaults to COPERT_SYSTEM_PROMPT)
        tools: Optional custom tool list of the main agent (defaults to ALL_TOOLS)
        approval_manager: Optional ApprovalManager for approving destructive operations

    Returns:
        Compiled StateGraph ready for invocation
    """
    # Use defaults if not provided
    if system_prompt is None:
        system_prompt = COPERT_SYSTEM_PROMPT
    if tools is None:
        tools = ALL_TOOLS

    # Initialize LLM with tools
    llm_client = create_llm()
    llm_with_tools = llm_client.bind_tools(tools)

    # Define the agent node
    def agent_node(state: AgentState) -> AgentState:
        """Agent node that calls the LLM with tools bound.

        The LLM can respond with:
        - Text only (no tool calls) → ends conversation
        - Tool calls (with optional text) → executes tools
        - After seeing tool results → generates summary

        Args:
            state: Current agent state containing messages

        Returns:
            Updated state with LLM response (AIMessage with content and/or tool_calls)
        """
        messages = state["messages"]

        # Add system prompt if this is the first interaction
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=system_prompt)] + messages

        # Invoke LLM with tools
        response = llm_with_tools.invoke(messages)

        return {"messages": [response]}

    # Create custom tool node with approval support if approval_manager is provided
    if approval_manager:
        def approval_tool_node(state: AgentState) -> AgentState:
            """Custom tool node that requests approval before executing destructive operations.

            Args:
                state: Current agent state containing messages

            Returns:
                Updated state with ToolMessage results
            """
            messages = state["messages"]
            last_message = messages[-1]

            if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
                return {"messages": []}

            # Process each tool call with approval check
            tool_messages = []
            tools_by_name = {tool.name: tool for tool in tools}

            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_id = tool_call.get("id")

                # Request approval
                approved = approval_manager.request_approval(tool_name, tool_args)

                if approved:
                    # Execute the tool
                    tool = tools_by_name.get(tool_name)
                    if tool:
                        try:
                            result = tool.invoke(tool_args)
                            tool_messages.append(
                                ToolMessage(
                                    content=str(result),
                                    name=tool_name,
                                    tool_call_id=tool_id,
                                )
                            )
                        except Exception as e:
                            tool_messages.append(
                                ToolMessage(
                                    content=f"Error: {str(e)}",
                                    name=tool_name,
                                    tool_call_id=tool_id,
                                )
                            )
                    else:
                        tool_messages.append(
                            ToolMessage(
                                content=f"Error: Tool '{tool_name}' not found",
                                name=tool_name,
                                tool_call_id=tool_id,
                            )
                        )
                else:
                    # User rejected the operation
                    tool_messages.append(
                        ToolMessage(
                            content=f"Operation rejected by user",
                            name=tool_name,
                            tool_call_id=tool_id,
                        )
                    )

            return {"messages": tool_messages}

        tool_node_func = approval_tool_node
    else:
        # Use standard ToolNode if no approval manager
        tool_node_func = ToolNode(tools)

    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Determine if we should continue to tools or end the conversation.

        This function checks if the last AI message contains tool calls.
        - If yes: route to "tools" to execute them
        - If no: route to "end" (agent has provided final text response)

        Args:
            state: Current agent state

        Returns:
            "tools" if the last message contains tool calls, "end" otherwise
        """
        messages = state["messages"]
        last_message = messages[-1]

        # If the LLM makes a tool call, route to tools
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"

        # Otherwise, end the conversation (agent has provided final text response)
        return "end"

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node_func)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",  # If agent wants to use tools
            "end": END,        # If agent provides final text response
        },
    )

    # IMPORTANT: After tools execute, always go back to agent
    # This allows the agent to see tool results and generate a summary message or choose to invoke another tool
    workflow.add_edge("tools", "agent")

    return workflow.compile()


def invoke_agent(user_input: str, history: list = None):
    """Convenience function to invoke the agent with a user message.

    Args:
        user_input: The user's input message
        history: Optional conversation history

    Returns:
        The complete agent state with all messages
    """
    graph = create_agent_graph()

    # Prepare messages
    messages = history or []
    messages.append(HumanMessage(content=user_input))

    # Invoke the graph
    result = graph.invoke({"messages": messages})

    return result
