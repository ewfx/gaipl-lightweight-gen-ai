import os
import asyncio
import chainlit as cl
import json

from typing import Literal
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain.schema.runnable.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


# Load environment variables
print("Loading environment variables...")
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("Missing OPENAI_API_KEY in .env!")
print("OPENAI_API_KEY loaded successfully.")

# MCP Server Path
MCP_SERVER_PATH = os.path.abspath("./elastic_mcp/mcp_server_servicenow/main.py")
SNOW_SERVER_PATH = os.path.abspath("./servicenow-mcp-main/src/servicenow_mcp/cli.py")
print(f"MCP server path: {MCP_SERVER_PATH}")

# ---------------------- Tools ----------------------

@tool
def elastic_tool(query: str) -> str:
    """All Elastic Search Related Functionality."""
    async def run_elastic_agent():
        try:
            server_params = StdioServerParameters(command="python", args=[MCP_SERVER_PATH])
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await load_mcp_tools(session)
                    model = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=openai_api_key)
                    agent = create_react_agent(model, tools)
                    result = await agent.ainvoke({"messages": query})
                    return result
        except Exception as e:
            return f"ElasticTool failed: {str(e)}"

    return asyncio.run(run_elastic_agent())

@tool
def service_now_tool(query: str) -> str:
    """All Service Now Related Functionality."""
    async def run_elastic_agent():
        try:
            server_params = StdioServerParameters(command="python", args=[SNOW_SERVER_PATH])
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await load_mcp_tools(session)
                    model = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=openai_api_key)
                    agent = create_react_agent(model, tools)
                    result = await agent.ainvoke({"messages": query})
                    return result
        except Exception as e:
            return f"ServiceNow Tool failed: {str(e)}"

    return asyncio.run(run_elastic_agent())

# ---------------------- LangGraph Agent Setup ----------------------

tools = [elastic_tool,service_now_tool]
llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0, openai_api_key=openai_api_key)
llm = llm.bind_tools(tools).with_config(system_prompt="""
You are a helpful assistant designed to resolve infrastructure incidents using available tools.
Use the tools `elastic_tool` and `service_now_tool` when relevant.
Refer to the incidents provided at the start of the session to give context-aware responses.
Only use tools if necessary, and summarize findings clearly for the user.
                                        
Examples of Service Now Tool Queries a
        - "find all incidents about SAP"
        - "search for incidents related to email"
        - "show me all incidents with high priority"
""")

tool_node = ToolNode(tools=tools)

def should_continue(state: MessagesState) -> Literal["tools", "final"]:
    last_message = state["messages"][-1]
    decision = "tools" if last_message.tool_calls else "final"
    print(f" should_continue decision: {decision}")
    return decision

def call_model(state: MessagesState):
    messages = state["messages"]
    print(f"LLM received messages: {[m.content for m in messages]}")
    response = llm.invoke(messages)
    print(f"LLM response: {response}")
    return {"messages": messages + [response]}

def pass_through_final(state: MessagesState):
    # Remove raw tool messages
    filtered = [msg for msg in state["messages"] if not isinstance(msg, ToolMessage)]
    if filtered and filtered[-1].content.strip():
        print("Final message (tool response filtered).")
        return {"messages": filtered}
    return {"messages": [AIMessage(content="No response generated.")]}



builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", tool_node)
builder.add_node("final", pass_through_final)
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "final")
builder.add_edge("final", END)
graph = builder.compile()

# ---------------------- Chainlit Session ----------------------
chat_history = {}

@cl.on_chat_start
async def on_chat_start():
    print("Chat started. Triggering getVisibleIncidents()...")
    fn = cl.CopilotFunction(name="getVisibleIncidents", args={})
    response = await fn.acall()
    incidents = response.get("incidents") if response else None
    if incidents:
        print(f"Received incidents from frontend: {len(incidents)}")
        incident_list = "\n".join([f"Incident #{i+1}: {inc['incidentnum']} — {inc['shortDescription']}" for i, inc in enumerate(incidents)])
        await cl.Message(content=f"Here are all the incidents currently visible on screen:\n\n{incident_list}").send()

    else:
        print("No incidents received from frontend.")
        await cl.Message(content="No incidents received from frontend.").send()

@cl.on_message
async def on_message(msg: cl.Message):
    session_id = cl.context.session.id
    config = {"configurable": {"thread_id": session_id}}
    cb = cl.LangchainCallbackHandler()

    # Initialize session history if not present
    if session_id not in chat_history:
        chat_history[session_id] = []

    # Add new user message to session history
    chat_history[session_id].append(HumanMessage(content=msg.content))

    final_answer = cl.Message(content="")
    full_response = ""
    streamed = False

    try:
        async for step, _ in graph.astream(
            {"messages": chat_history[session_id]},
            stream_mode="messages",
            config=RunnableConfig(callbacks=[cb], **config),
        ):
            if hasattr(step, "type") and step.type == "tool":
                continue
            if step and getattr(step, "content", "").strip():
                streamed = True
                full_response += step.content
                await final_answer.stream_token(step.content)

        # Append AI response to session memory
        chat_history[session_id].append(AIMessage(content=full_response.strip()))

    except Exception as e:
        final_answer.content = f"Error: {e}"
        await final_answer.send()
    else:
        if not streamed:
            final_answer.content = full_response.strip()
            await final_answer.send()

@cl.on_chat_end
def on_chat_end():
    session_id = cl.context.session.id
    if session_id in chat_history:
        del chat_history[session_id]
