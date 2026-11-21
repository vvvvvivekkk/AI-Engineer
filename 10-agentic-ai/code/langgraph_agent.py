"""
langgraph_agent.py - a tool-using agent built as a LangGraph state graph.

Checked against langgraph 1.2.x and langchain-core 1.8.x (late 2026).

Vocabulary
----------
State       : a dictionary that flows through the graph (here: the list of messages).
Node        : a Python function that receives the state and returns an update.
Edge        : a fixed arrow "after node A, go to node B".
Conditional : an arrow whose target is chosen at run time by a function.
Checkpointer: saves the state after every step, so a conversation ("thread")
              can continue later - this is the agent's short-term memory.

Offline by default: the "llm" node is a rule-based stand-in that emits a tool call.
If ANTHROPIC_API_KEY is set and langchain-anthropic is installed, a real model is used.

Run: python langgraph_agent.py
"""
import os

from langchain_core.messages import AIMessage, HumanMessage   # message types used by LangGraph
from langchain_core.tools import tool                          # decorator that turns a function into a tool
from langgraph.checkpoint.memory import InMemorySaver          # keeps checkpoints in RAM
from langgraph.graph import START, MessagesState, StateGraph   # graph building blocks
from langgraph.prebuilt import ToolNode, tools_condition       # ready-made "run tools" node and router


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""                  # the docstring becomes the tool description
    return {"taipei": "Sunny, 24C", "london": "Rainy, 9C"}.get(city.lower(), "Cloudy, 20C")


@tool
def convert_c_to_f(celsius: float) -> float:
    """Convert a Celsius temperature to Fahrenheit."""
    return round(celsius * 9 / 5 + 32, 1)


TOOLS = [get_weather, convert_c_to_f]


def fake_llm(state: MessagesState) -> dict:
    """Offline stand-in for a chat model. It decides based on the last message."""
    last = state["messages"][-1]
    if isinstance(last, HumanMessage):                           # new question -> ask for a tool
        city = "Taipei" if "taipei" in last.content.lower() else "London"
        return {"messages": [AIMessage(content="", tool_calls=[
            {"name": "get_weather", "args": {"city": city}, "id": "call_1"}])]}
    return {"messages": [AIMessage(content=f"Here is what I found: {last.content}")]}  # tool result -> answer


def make_llm_node():
    """Return a real model node if possible, else the fake one."""
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            from langchain_anthropic import ChatAnthropic          # pip install langchain-anthropic
            model = ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")).bind_tools(TOOLS)
            return lambda state: {"messages": [model.invoke(state["messages"])]}
        except ImportError:
            print("langchain-anthropic not installed - using the offline stand-in")
    return fake_llm


def build_app():
    graph = StateGraph(MessagesState)                # state = {"messages": [...]} with append behaviour
    graph.add_node("llm", make_llm_node())           # node 1: the "brain"
    graph.add_node("tools", ToolNode(TOOLS))         # node 2: runs whatever tool calls the llm made
    graph.add_edge(START, "llm")                     # start at the llm
    graph.add_conditional_edges("llm", tools_condition)  # tool calls? -> "tools", else -> END
    graph.add_edge("tools", "llm")                   # after tools, go back to the llm (the loop)
    return graph.compile(checkpointer=InMemorySaver())   # compile = freeze into a runnable app


if __name__ == "__main__":
    app = build_app()
    config = {"configurable": {"thread_id": "demo-1"}}   # thread_id names one conversation
    result = app.invoke({"messages": [HumanMessage("What's the weather in Taipei?")]}, config)
    for m in result["messages"]:
        print(f"{type(m).__name__:12} {m.content!r} {getattr(m, 'tool_calls', '') or ''}")
    print("\nMermaid source of the graph:\n", app.get_graph().draw_mermaid())
